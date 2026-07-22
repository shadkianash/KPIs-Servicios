import datetime as dt
import hashlib
import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.etl.core.models import (
    ETLError,
    IdempotencyError,
    ImportContext,
    ImportResult,
)
from app.etl.loaders.database_loader import DatabaseLoader
from app.etl.parsers.csv_reader import CSVReader
from app.etl.registry.schema_registry import schema_registry
from app.etl.transformers.transformer import Transformer
from app.etl.validators.row_validator import RowValidator
from app.etl.validators.schema_validator import SchemaValidator
from app.models.staging import ImportJob

logger = logging.getLogger(__name__)


class ImportService:
    """Master orchestrator for the CSAP CSV ETL Import pipeline."""

    def __init__(self) -> None:
        self.csv_reader = CSVReader()
        self.schema_validator = SchemaValidator()
        self.row_validator = RowValidator()
        self.transformer = Transformer()
        self.db_loader = DatabaseLoader()

    async def import_file(
        self,
        session: AsyncSession,
        file_name: str,
        content_bytes: bytes,
        schema_name: str,
        correlation_id: str | None = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> ImportResult:
        """Executes the complete, idempotent, and resilient import pipeline."""
        start_time_ns = time.perf_counter_ns()

        # 1. Initialize Context
        corr_id = correlation_id or f"etl-{uuid.uuid4()}"
        now_utc = dt.datetime.now(dt.UTC).replace(tzinfo=None)
        context = ImportContext(correlation_id=corr_id, started_at=now_utc)

        # 2. Check File Duplicate Protection via SHA256 Checksum
        checksum = self._calculate_checksum(content_bytes)
        dup_stmt = select(ImportJob).where(ImportJob.checksum_sha256 == checksum)
        dup_result = await session.execute(dup_stmt)
        if dup_result.scalar_one_or_none() is not None:
            raise IdempotencyError(
                f"File '{file_name}' with checksum {checksum} has already "
                "been imported."
            )

        # 3. Retrieve Schema Definition
        schema = schema_registry.get_schema(schema_name)

        # 4. Create and Save initial ImportJob Tracking Entity
        job_id = uuid.uuid4()
        job = ImportJob(
            job_id=job_id,
            import_batch_id=context.import_batch_id,
            source_system=context.source_system,
            connector_name=context.connector_name,
            file_name=file_name,
            original_file_name=file_name,
            checksum_sha256=checksum,
            started_at=context.started_at,
            status="RUNNING",
            correlation_id=context.correlation_id,
        )
        session.add(job)
        await session.commit()

        result = ImportResult(
            job_id=job_id,
            import_batch_id=context.import_batch_id,
            file_name=file_name,
            original_file_name=file_name,
            checksum_sha256=checksum,
            started_at=context.started_at,
        )

        logger.info(
            f"[{context.correlation_id}] Starting ImportJob {job_id} "
            f"for file: {file_name}"
        )

        try:
            # Step 1: Read and Standardize CSV to DataFrame
            df = self.csv_reader.read(
                content_bytes=content_bytes,
                schema=schema,
                delimiter=delimiter,
                encoding=encoding,
            )
            result.processed_rows = len(df)

            if df.is_empty():
                # Clean empty files gracefully
                await self._finalize_job(
                    session, job, result, "COMPLETED", start_time_ns
                )
                return result

            # Step 2: Validate Schema Integrity
            self.schema_validator.validate(df, schema)

            # Step 3: Validate Row Constraint Logic
            valid_df, failures = self.row_validator.validate_rows(df, schema)
            result.failures = failures
            result.invalid_rows = len(df) - len(valid_df)

            # Step 4: Transform Data types and Normalize
            transformed_records = self.transformer.transform(valid_df, schema)

            # Step 5: Database Persistence Load
            inserted, updated, skipped, duplicated = await self.db_loader.load_staging(
                session=session,
                records=transformed_records,
                schema=schema,
                job_id=job_id,
            )

            result.imported_rows = inserted
            result.updated_rows = updated
            result.skipped_rows = skipped
            result.duplicated_rows = duplicated + result.invalid_rows

            # 5. Finalize successfully completed job
            await self._finalize_job(session, job, result, "COMPLETED", start_time_ns)
            logger.info(
                f"[{context.correlation_id}] Finished ImportJob {job_id}. "
                f"Imported: {result.imported_rows}, "
                f"Updated: {result.updated_rows}, "
                f"Invalid: {result.invalid_rows}"
            )
            return result

        except Exception as e:
            # Fail Loudly: update job status, log detail, and raise
            error_msg = str(e)
            result.status = "FAILED"
            result.error_message = error_msg
            logger.error(
                f"[{context.correlation_id}] Fatal pipeline error on "
                f"ImportJob {job_id}: {error_msg}",
                exc_info=True,
            )
            await self._finalize_job(
                session, job, result, "FAILED", start_time_ns, error_msg
            )

            if isinstance(e, ETLError):
                raise e
            raise ETLError(
                f"Fatal error during CSV Import pipeline execution: {e}"
            ) from e

    def _calculate_checksum(self, data: bytes) -> str:
        """Returns hex encoded SHA256 of raw data bytes."""
        return hashlib.sha256(data).hexdigest()

    async def _finalize_job(
        self,
        session: AsyncSession,
        job: ImportJob,
        result: ImportResult,
        status: str,
        start_time_ns: int,
        error_msg: str | None = None,
    ) -> None:
        """Refreshes and persists tracking counts, status, and duration."""
        duration_ms = (time.perf_counter_ns() - start_time_ns) // 1_000_000

        result.finished_at = dt.datetime.now(dt.UTC).replace(tzinfo=None)
        result.duration_ms = duration_ms
        result.status = status
        result.error_message = error_msg

        # Bind metrics back to DB model
        job.finished_at = result.finished_at
        job.duration_ms = duration_ms
        job.processed_rows = result.processed_rows
        job.imported_rows = result.imported_rows
        job.updated_rows = result.updated_rows
        job.skipped_rows = result.skipped_rows
        job.duplicated_rows = result.duplicated_rows
        job.invalid_rows = result.invalid_rows
        job.status = status
        job.error_message = error_msg

        session.add(job)
        await session.commit()
