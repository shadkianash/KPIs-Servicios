from app.etl.schemas.base import BaseSchema, ColumnDefinition


class TicketHistorySchema(BaseSchema):
    """Schema definition for Archer Ticket History.

    TODO: Update and extend once final real-world Archer Ticket History export
    columns, headers, and encoding parameters are provided.
    """

    name = "ticket_history"
    version = "1.0.0"
    primary_key = "history_id"

    @property
    def columns(self) -> list[ColumnDefinition]:
        return [
            ColumnDefinition(
                name="history_id",
                target_type="string",
                required=True,
                aliases=["history id", "id", "audit_id"],
            ),
            ColumnDefinition(
                name="ticket_id",
                target_type="string",
                required=True,
                aliases=["ticket id", "ticket_ref"],
            ),
            ColumnDefinition(
                name="change_date",
                target_type="datetime",
                required=False,
                aliases=["change date", "date_changed", "modified_at"],
            ),
            ColumnDefinition(
                name="field_changed",
                target_type="string",
                required=False,
                aliases=["field name", "field changed", "property"],
            ),
            ColumnDefinition(
                name="old_value",
                target_type="string",
                required=False,
                aliases=["old value", "from_value"],
            ),
            ColumnDefinition(
                name="new_value",
                target_type="string",
                required=False,
                aliases=["new value", "to_value"],
            ),
        ]
