from unittest import mock
from fluidly.sqlalchemy.timestamp_mixin import TimestampMixin

from fluidly.sqlalchemy.upsert import (
    ConflictAction,
    get_on_conflict_stmt,
    update_required,
)
import sqlalchemy as db
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SomeModel(Base):
    __tablename__ = "some_model"

    id = db.Column(db.Integer, primary_key=True)


class TimestampModel(TimestampMixin, Base):
    __tablename__ = "timestamp_model"

    id = db.Column(db.Integer, primary_key=True)


def format_statement(s):
    try:
        s = s.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    except AttributeError:
        s = str(s).replace("\n", "")

    return str(s)


class TestGetOnConflictStmt:
    def test_upsert(self):
        some_model_table = SomeModel.__table__

        stmt = insert(some_model_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], ["id"], where=stmt.excluded.id == some_model_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO some_model (id) VALUES (1) ON CONFLICT (id) DO UPDATE SET id = excluded.id WHERE excluded.id = some_model.id"
        )

    def test_upsert_with_timestamp_mixin(self):
        timestamp_model_table = TimestampModel.__table__

        stmt = insert(timestamp_model_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], ["id"], where=stmt.excluded.id == timestamp_model_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO timestamp_model (last_seen_at, first_seen_at, id) VALUES (now(), now(), 1) ON CONFLICT (id) DO UPDATE SET last_seen_at = %(param_1)s, id = excluded.id WHERE excluded.id = timestamp_model.id"
        )

    def test_does_nothing_if_no_arguments(self):
        some_model_table = SomeModel.__table__

        stmt = insert(some_model_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], [], where=stmt.excluded.id == some_model_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO some_model (id) VALUES (1) ON CONFLICT (id) DO NOTHING"
        )

    def test_does_nothing_if_do_nothing_action_was_passed(self):
        some_model_table = SomeModel.__table__

        stmt = insert(some_model_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt,
            ["id"],
            ["id"],
            where=stmt.excluded.id == some_model_table.c.id,
            action=ConflictAction.DO_NOTHING,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO some_model (id) VALUES (1) ON CONFLICT (id) DO NOTHING"
        )

    def test_not_passing_where_clause(self):
        some_model_table = SomeModel.__table__

        stmt = insert(some_model_table).values(id=1)
        stmt = get_on_conflict_stmt(stmt, ["id"], ["id"])
        assert (
            format_statement(stmt)
            == "INSERT INTO some_model (id) VALUES (1) ON CONFLICT (id) DO UPDATE SET id = excluded.id"
        )


def test_update_required_refresh_data_true_return_false():
    normalised_table = mock.MagicMock()
    stmt = mock.MagicMock()

    normalised_table.c.updated_at = 2
    stmt.excluded.updated_at = 1

    result = update_required(normalised_table, stmt, True)

    assert result is False


def test_update_required_refresh_data_true_return_true():
    normalised_table = mock.MagicMock()
    stmt = mock.MagicMock()

    normalised_table.c.updated_at = 2
    stmt.excluded.updated_at = 2

    result = update_required(normalised_table, stmt, True)

    assert result is True


def test_update_required_refresh_data_false_return_true():
    normalised_table = mock.MagicMock()
    stmt = mock.MagicMock()

    normalised_table.c.updated_at = 1
    stmt.excluded.updated_at = 2

    result = update_required(normalised_table, stmt, False)

    assert result is True


def test_update_required_refresh_data_false_return_false():
    normalised_table = mock.MagicMock()
    stmt = mock.MagicMock()

    normalised_table.c.updated_at = 2
    stmt.excluded.updated_at = 1

    result = update_required(normalised_table, stmt, False)

    assert result is False
