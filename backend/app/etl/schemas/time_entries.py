from app.etl.schemas.base import BaseSchema, ColumnDefinition


class TimeEntriesSchema(BaseSchema):
    """Schema definition for Archer Time Entries.

    TODO: Update and extend once final real-world Archer Time Entries export
    columns, headers, and encoding parameters are provided.
    """

    name = "time_entries"
    version = "1.0.0"
    primary_key = "entry_id"

    @property
    def columns(self) -> list[ColumnDefinition]:
        return [
            ColumnDefinition(
                name="entry_id",
                target_type="string",
                required=True,
                aliases=["entry id", "id", "log_id"],
            ),
            ColumnDefinition(
                name="ticket_id",
                target_type="string",
                required=True,
                aliases=["ticket id", "ticket_ref"],
            ),
            ColumnDefinition(
                name="user_id",
                target_type="string",
                required=False,
                aliases=["user id", "worker_id", "author"],
            ),
            ColumnDefinition(
                name="work_date",
                target_type="datetime",
                required=False,
                aliases=["work date", "date", "logged_at"],
            ),
            ColumnDefinition(
                name="hours_spent",
                target_type="float",
                required=False,
                aliases=["hours spent", "duration", "hours"],
            ),
            ColumnDefinition(
                name="activity_type",
                target_type="string",
                required=False,
                aliases=["activity type", "category", "type"],
            ),
        ]
