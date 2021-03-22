from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import Column, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import Insert


class ConflictAction(Enum):
    DO_NOTHING = "DO_NOTHING"
    DO_UPDATE = "DO_UPDATE"


def get_on_conflict_stmt(
    stmt: Insert,
    index: Any,
    args: Any,
    where: Any = None,
    action: ConflictAction = ConflictAction.DO_UPDATE,
) -> Insert:
    values = {attr: getattr(stmt.excluded, attr) for attr in args}

    if hasattr(stmt.table.c, "last_seen_at") and "last_seen_at" not in values:
        values["last_seen_at"] = datetime.utcnow()

    if not args or action == ConflictAction.DO_NOTHING:
        return stmt.on_conflict_do_nothing(index_elements=index)

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
    new_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    table: Table,
    refresh_data: bool = False,
    returning: Optional[List[Column]] = None,
    action: ConflictAction = ConflictAction.DO_UPDATE,
) -> Insert:
    """Constructs an upserts statement with fields in database based on
    incoming message.

    Args:
        indexes: List of indexes to upsert on.
        keys_mapping: Mapping of message keys to column names values.
        new_data: Dictionary containing new entity's data.
        table: SqlAlchemy table to be updated.
        refresh_data: Should we upsert when updated_at is the same?
        action: On conflict action to be perfomed.
    """

    message_attributes = set(keys_mapping.keys())
    column_names = set(keys_mapping.values())

    keys_to_insert = column_names
    keys_to_update = keys_to_insert - set(indexes)

    if isinstance(new_data, Mapping):
        values_to_insert = {
            keys_mapping[attribute]: new_data.get(attribute)
            for attribute in message_attributes
        }
        stmt = insert(table).values(values_to_insert)
    else:
        list_to_insert = [
            {
                keys_mapping[attribute]: datum.get(attribute)
                for attribute in message_attributes
            }
            for datum in new_data
        ]
        stmt = insert(table).values(list_to_insert)

    stmt = get_on_conflict_stmt(
        stmt=stmt,
        index=indexes,
        args=keys_to_update,
        where=update_required(table, stmt, refresh_data),
        action=action,
    )

    if returning:
        stmt = stmt.returning(*returning)

    return stmt
