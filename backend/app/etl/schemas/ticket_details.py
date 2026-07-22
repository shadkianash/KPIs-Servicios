from app.etl.schemas.base import BaseSchema, ColumnDefinition


class TicketDetailsSchema(BaseSchema):
    """Schema definition for Archer Ticket Details.

    TODO: Update and extend once final real-world Archer Ticket Details export
    columns, headers, and encoding parameters are provided.
    """

    name = "ticket_details"
    version = "1.0.0"
    primary_key = "ticket_id"

    @property
    def columns(self) -> list[ColumnDefinition]:
        return [
            ColumnDefinition(
                name="ticket_id",
                target_type="string",
                required=True,
                aliases=["ticket id", "id", "ref_num"],
            ),
            ColumnDefinition(
                name="title",
                target_type="string",
                required=False,
                aliases=["subject", "summary"],
            ),
            ColumnDefinition(
                name="description",
                target_type="string",
                required=False,
                aliases=["notes", "desc"],
            ),
            ColumnDefinition(
                name="created_date",
                target_type="datetime",
                required=False,
                aliases=["created date", "open date", "created_at"],
            ),
            ColumnDefinition(
                name="closed_date",
                target_type="datetime",
                required=False,
                aliases=["closed date", "close date", "closed_at"],
            ),
            ColumnDefinition(
                name="status",
                target_type="string",
                required=False,
                aliases=["state"],
                default_value="New",
            ),
            ColumnDefinition(
                name="assigned_team",
                target_type="string",
                required=False,
                aliases=["team", "group", "assigned team"],
            ),
        ]
