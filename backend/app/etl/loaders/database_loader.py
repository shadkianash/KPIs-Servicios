import uuid
from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.etl.schemas.base import BaseSchema
from app.models.staging import (
    StagingTicketDetail,
    StagingTicketHistory,
    StagingTimeEntry,
)


class DatabaseLoader:
    """Loads transformed staging records into relational database tables."""

    MODEL_MAPPING: dict[str, type[Base]] = {
        "ticket_details": StagingTicketDetail,
        "ticket_history": StagingTicketHistory,
        "time_entries": StagingTimeEntry,
    }

    async def load_staging(
        self,
        session: AsyncSession,
        records: list[dict[str, Any]],
        schema: BaseSchema,
        job_id: uuid.UUID,
    ) -> tuple[int, int, int, int]:
        """Loads records into DB.

        Returns tuple of (inserted, updated, skipped, duplicated).
        """
        if not records:
            return 0, 0, 0, 0

        model_cls = self.MODEL_MAPPING.get(schema.name)
        if not model_cls:
            raise ValueError(f"No staging model registered for schema: {schema.name}")

        pk_col = schema.primary_key
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        duplicated_count = 0

        # Extract list of incoming business keys
        incoming_keys = [str(r[pk_col]) for r in records if r.get(pk_col) is not None]
        if not incoming_keys:
            return 0, 0, 0, 0

        # Query existing business keys in staging table for this specific PK
        stmt = select(getattr(model_cls, pk_col)).where(
            getattr(model_cls, pk_col).in_(incoming_keys)
        )
        result = await session.execute(stmt)
        existing_keys = {str(row[0]) for row in result.all()}

        # Partition records into Inserts and Updates
        inserts_to_make = []
        updates_to_make = []

        for record in records:
            rec_copy = record.copy()
            rec_copy["job_id"] = job_id
            key_val = str(rec_copy[pk_col])

            if key_val in existing_keys:
                updates_to_make.append(rec_copy)
            else:
                inserts_to_make.append(rec_copy)

        # Execute inserts in a single bulk batch
        if inserts_to_make:
            await session.execute(insert(model_cls), inserts_to_make)
            inserted_count += len(inserts_to_make)

        # Execute updates (running updates safely)
        if updates_to_make:
            for upd_rec in updates_to_make:
                key_val = upd_rec[pk_col]
                await session.execute(
                    update(model_cls)
                    .where(getattr(model_cls, pk_col) == key_val)
                    .values(upd_rec)
                )
            updated_count += len(updates_to_make)

        return inserted_count, updated_count, skipped_count, duplicated_count
