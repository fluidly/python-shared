from sqlalchemy.sql import Insert


def get_on_conflict_stmt(stmt: Insert, index, args, where) -> Insert:
    return stmt.on_conflict_do_update(
        index_elements=index,
        set_={attr: getattr(stmt.excluded, attr) for attr in args},
        where=where,
    )


def update_required(normalised_table, stmt, refresh_data):
    return (
        stmt.excluded.updated_at > normalised_table.c.updated_at
        if not refresh_data
        else stmt.excluded.updated_at >= normalised_table.c.updated_at
    )
