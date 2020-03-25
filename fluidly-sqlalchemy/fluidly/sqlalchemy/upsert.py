from typing import Any

from sqlalchemy.sql import Insert


def get_on_conflict_stmt(stmt: Insert, index: Any, args: Any, where: Any) -> Insert:
    return stmt.on_conflict_do_update(
        index_elements=index,
        set_={attr: getattr(stmt.excluded, attr) for attr in args},
        where=where,
    )


def update_required(normalised_table: Any, stmt: Any, refresh_data: bool) -> Any:
    return (
        stmt.excluded.updated_at > normalised_table.c.updated_at
        if not refresh_data
        else stmt.excluded.updated_at >= normalised_table.c.updated_at
    )
