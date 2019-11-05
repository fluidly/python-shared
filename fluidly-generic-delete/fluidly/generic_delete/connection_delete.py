from fluidly.structlog.pubsub_helper import pubsub_log_entrypoint_class
from sqlalchemy import delete


class DeleteConnectionConsumer:
    def __init__(self, base):
        self.base = base

    @pubsub_log_entrypoint_class
    def delete_by_connection_id(self, session, message, refresh_generated=False):
        connection_id = message.connection_id
        for table in self.base.metadata.tables.values():
            if table.c.get("connection_id") is not None:
                session.execute(
                    delete(table).where(table.c.connection_id == connection_id)
                )

        session.commit()
