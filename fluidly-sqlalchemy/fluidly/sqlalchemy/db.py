from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import SessionTransaction

sessionmaker = sessionmaker()


@contextmanager
def db_session() -> Generator[SessionTransaction, Any, Any]:
    try:
        session: SessionTransaction = sessionmaker()
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
