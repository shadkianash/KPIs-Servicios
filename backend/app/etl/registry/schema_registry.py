from app.etl.schemas.base import BaseSchema
from app.etl.schemas.ticket_details import TicketDetailsSchema
from app.etl.schemas.ticket_history import TicketHistorySchema
from app.etl.schemas.time_entries import TimeEntriesSchema


class SchemaRegistry:
    """Registry pattern that indexes configured schemas for ETL imports."""

    def __init__(self) -> None:
        self._registry: dict[str, BaseSchema] = {}
        # Register standard default schemas
        self.register(TicketDetailsSchema())
        self.register(TicketHistorySchema())
        self.register(TimeEntriesSchema())

    def register(self, schema: BaseSchema) -> None:
        """Register a new schema instance."""
        self._registry[schema.name] = schema

    def get_schema(self, name: str) -> BaseSchema:
        """Retrieve a registered schema by name."""
        if name not in self._registry:
            available = list(self._registry.keys())
            raise KeyError(f"Schema '{name}' is not registered. Available: {available}")
        return self._registry[name]


# Global singleton instance
schema_registry = SchemaRegistry()
