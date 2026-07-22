from typing import Any


class ChangeDetector:
    """Detects field-level differences between staging and production."""

    @staticmethod
    def detect_changes(
        existing_model: Any,
        incoming_data: dict[str, Any],
        exclude_fields: set[str] | None = None,
    ) -> tuple[bool, dict[str, dict[str, Any]]]:
        """Compares incoming fields with existing attributes."""
        exclude = exclude_fields or set()
        exclude.update({"id", "created_at", "updated_at", "job_id"})

        changes: dict[str, dict[str, Any]] = {}
        has_changed = False

        for field, new_val in incoming_data.items():
            if field in exclude:
                continue

            if not hasattr(existing_model, field):
                continue

            old_val = getattr(existing_model, field)

            # Compare value differences with type/None safeguards
            if old_val != new_val:
                has_changed = True
                changes[field] = {
                    "old": old_val,
                    "new": new_val,
                }

        return has_changed, changes
