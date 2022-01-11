from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session

from fluidly.pubsub.message import Message
from fluidly.structlog.pubsub_helper import pubsub_log_entrypoint_class


class DeleteConnectionConsumer:
    def __init__(
        self, base: DeclarativeMeta, ignored_tables: Optional[List[str]] = None
    ):
        self.base = base
        if ignored_tables is None:
            self.ignored_tables = []
        else:
            self.ignored_tables = ignored_tables

    @pubsub_log_entrypoint_class
    def delete_by_connection_id(
        self, session: Session, message: Message, refresh_generated: bool = False
    ) -> None:
        connection_id = message.connection_id
        for table in self.base.metadata.tables.values():
            if (
                table.name not in self.ignored_tables
                and table.c.get("connection_id") is not None
            ):
                session.execute(
                    delete(table).where(table.c.connection_id == connection_id)
                )

        session.commit()
