import sqlalchemy as db
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base

from fluidly.sqlalchemy.db import db_session
from fluidly.sqlalchemy.timestamp_mixin import TimestampMixin

Base = declarative_base()


class SomeModel(TimestampMixin, Base):
    __tablename__ = "some_model"

    id = db.Column(db.Integer, primary_key=True)


def format_statement(s):
    try:
        s = s.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    except AttributeError:
        s = str(s).replace("\n", "")

    return str(s)


def test_select():
    with db_session() as session:
        stmt = session.query(SomeModel)
        assert (
            format_statement(stmt)
            == "SELECT some_model.last_seen_at AS some_model_last_seen_at, some_model.first_seen_at AS some_model_first_seen_at, some_model.id AS some_model_id FROM some_model"
        )


def test_insert():
    stmt = insert(SomeModel.__table__).values(id=1)
    assert (
        format_statement(stmt)
        == "INSERT INTO some_model (last_seen_at, first_seen_at, id) VALUES (now(), now(), 1)"
    )
