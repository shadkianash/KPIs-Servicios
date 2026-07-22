from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ColumnDefinition:
    """Configures validation, parsing, and type definitions for a single column."""

    name: str
    target_type: str  # "string", "int", "float", "datetime", "uuid", "bool"
    required: bool = True
    aliases: list[str] = field(default_factory=list)
    default_value: Any = None
    parser_rule: str | None = None  # e.g., "trim", "uppercase", "date_iso"


class BaseSchema:
    """Abstract base definition for a versioned CSV import schema."""

    name: str = "base"
    version: str = "1.0.0"
    primary_key: str = "id"

    @property
    def columns(self) -> list[ColumnDefinition]:
        """List of all column definitions for this schema."""
        raise NotImplementedError("Schemas must implement column definitions.")

    @property
    def required_columns(self) -> list[str]:
        """List of column names that must be present in the source CSV."""
        return [c.name for c in self.columns if c.required]

    @property
    def column_types(self) -> dict[str, str]:
        """Map of column names to target data types."""
        return {c.name: c.target_type for c in self.columns}

    @property
    def default_values(self) -> dict[str, Any]:
        """Map of column names to default values."""
        return {
            c.name: c.default_value for c in self.columns if c.default_value is not None
        }

    @property
    def aliases(self) -> dict[str, str]:
        """Reverse map of aliases to their standardized schema column name."""
        alias_map = {}
        for c in self.columns:
            for alias in c.aliases:
                alias_map[alias.lower()] = c.name
        return alias_map
