from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

SessionMaker = sessionmaker()


@contextmanager
def db_session() -> Generator[Session, Any, Any]:
    try:
        session = SessionMaker()
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
