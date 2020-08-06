from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import ResultProxy
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import Insert

from fluidly.pubsub.message import Message


def get_on_conflict_stmt(stmt: Insert, index: Any, args: Any, where: Any) -> Insert:
    values = {attr: getattr(stmt.excluded, attr) for attr in args}

    if hasattr(stmt.table.c, "last_seen_at") and "last_seen_at" not in values:
        values["last_seen_at"] = datetime.utcnow()

    return stmt.on_conflict_do_update(index_elements=index, set_=values, where=where)


def update_required(normalised_table: Any, stmt: Any, refresh_data: bool) -> Any:
    return (
        stmt.excluded.updated_at > normalised_table.c.updated_at
        if not refresh_data
        else stmt.excluded.updated_at >= normalised_table.c.updated_at
    )


def upsert_entity(
    indexes: List[str],
    keys_mapping: Dict[str, str],
    message: Message,
    table: Table,
    session: Session,
    refresh_data: bool = False,
    return_inserted: bool = False,
    returning: Optional[List[Column]] = None,
) -> ResultProxy:
    """Upserts fields in db based on incoming message
    Args:
        indexes: List of indexes to upsert on.
        keys_mapping: Mapping of message keys to column names values.
        message: Message containing data.
        table: SqlAlchemy table to be updated.
        session: SqlAlchemy db session.
        refresh_data: Should we upsert when updated_at is the same?
)
    """

    message_attributes = set(keys_mapping.keys())
    column_names = set(keys_mapping.values())

    keys_to_insert = column_names
    keys_to_update = keys_to_insert - set(indexes)

    values_to_insert = {
        keys_mapping[attribute]: message.data.get(attribute)
        for attribute in message_attributes
    }

    stmt = insert(table).values(values_to_insert)
    stmt = get_on_conflict_stmt(
        stmt, indexes, keys_to_update, where=update_required(table, stmt, refresh_data)
    )

    if returning:
        stmt = stmt.returning(*returning)

    return session.execute(stmt)
