from typing import Any

from pydantic import BaseModel, Field


class PaginationInfo(BaseModel):
    """Paging metadata descriptor."""

    page: int = Field(..., description="Active page number (1-based).")
    page_size: int = Field(..., description="Number of items returned per page.")
    total_records: int = Field(
        ..., description="Total count matching search parameters."
    )
    total_pages: int = Field(..., description="Total pages available.")


class ResponseEnvelope[T](BaseModel):
    """Standardized top-level REST response envelope wrapper."""

    success: bool = Field(True, description="Indicates if the API call succeeded.")
    data: T = Field(..., description="Main data payload.")
    pagination: PaginationInfo | None = Field(
        None, description="Pagination metadata, populated for paginated lists."
    )


class ErrorDetail(BaseModel):
    """Specific error descriptor."""

    code: str = Field(..., description="Systematic error code classifier.")
    message: str = Field(..., description="Detailed explanatory text.")
    details: Any | None = Field(None, description="Optional diagnostic details.")


class ErrorEnvelope(BaseModel):
    """Standardized top-level REST error envelope wrapper."""

    success: bool = Field(False, description="Always False for error envelopes.")
    error: ErrorDetail = Field(..., description="Top-level error descriptor.")
