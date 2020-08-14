import sqlalchemy as db
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base

from fluidly.sqlalchemy.db import db_session
from fluidly.sqlalchemy.materialised_view_mixin import MaterialisedViewMixin
from fluidly.sqlalchemy.upsert import get_on_conflict_stmt

Base = declarative_base()


class SomeModel(MaterialisedViewMixin, Base):
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
            == "SELECT some_model.view_generated_at AS some_model_view_generated_at, some_model.id AS some_model_id FROM some_model"
        )


def test_insert():
    stmt = insert(SomeModel.__table__).values(id=1)
    assert (
        format_statement(stmt)
        == "INSERT INTO some_model (view_generated_at, id) VALUES (now(), 1)"
    )


def test_upsert():
    table = SomeModel.__table__
    stmt = insert(table).values(id=1)
    stmt = get_on_conflict_stmt(
        stmt, ["id"], ["id"], where=stmt.excluded.id == table.c.id
    )
    assert (
        format_statement(stmt)
        == "INSERT INTO some_model (view_generated_at, id) VALUES (now(), 1) ON CONFLICT (id) DO UPDATE SET id = excluded.id WHERE excluded.id = some_model.id"
    )
