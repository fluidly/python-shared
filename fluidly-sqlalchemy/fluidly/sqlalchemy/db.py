from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

sessionmaker = sessionmaker()


@contextmanager
def db_session():
    try:
        session = sessionmaker()
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
