from unittest import mock

import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base

from fluidly.sqlalchemy.timestamp_mixin import TimestampMixin
from fluidly.sqlalchemy.upsert import (
    ConflictAction,
    get_on_conflict_stmt,
    update_required,
    upsert_entity,
)

Base = declarative_base()


def format_statement(s):
    try:
        s = s.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    except AttributeError:
        s = str(s).replace("\n", "")

    return str(s)


class TestGetOnConflictStmt:
    class SomeModel(Base):
        __tablename__ = "conflict_model"

        id = db.Column(db.Integer, primary_key=True)

    some_table = SomeModel.__table__

    class TimestampModel(TimestampMixin, Base):
        __tablename__ = "timestamp_model"

        id = db.Column(db.Integer, primary_key=True)

    timestamp_table = TimestampModel.__table__

    def test_upsert(self):
        stmt = insert(self.some_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], ["id"], where=stmt.excluded.id == self.some_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO conflict_model (id) VALUES (1) ON CONFLICT (id) DO UPDATE SET id = excluded.id WHERE excluded.id = conflict_model.id"
        )

    def test_upsert_with_timestamp_mixin(self):
        stmt = insert(self.timestamp_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], ["id"], where=stmt.excluded.id == self.timestamp_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO timestamp_model (last_seen_at, first_seen_at, id) VALUES (now(), now(), 1) ON CONFLICT (id) DO UPDATE SET last_seen_at = %(param_1)s, id = excluded.id WHERE excluded.id = timestamp_model.id"
        )

    def test_does_nothing_if_no_arguments(self):
        stmt = insert(self.some_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt, ["id"], [], where=stmt.excluded.id == self.some_table.c.id
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO conflict_model (id) VALUES (1) ON CONFLICT (id) DO NOTHING"
        )

    def test_does_nothing_if_do_nothing_action_was_passed(self):
        stmt = insert(self.some_table).values(id=1)
        stmt = get_on_conflict_stmt(
            stmt,
            ["id"],
            ["id"],
            where=stmt.excluded.id == self.some_table.c.id,
            action=ConflictAction.DO_NOTHING,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO conflict_model (id) VALUES (1) ON CONFLICT (id) DO NOTHING"
        )

    def test_not_passing_where_clause(self):
        stmt = insert(self.some_table).values(id=1)
        stmt = get_on_conflict_stmt(stmt, ["id"], ["id"])
        assert (
            format_statement(stmt)
            == "INSERT INTO conflict_model (id) VALUES (1) ON CONFLICT (id) DO UPDATE SET id = excluded.id"
        )


class TestUpsertEntity:
    class SomeModel(Base):
        __tablename__ = "upsert_model"

        id = db.Column(db.Integer, primary_key=True)
        updated_at = db.Column(db.DateTime, nullable=False)

    some_table = SomeModel.__table__

    def test_upsert_with_mapping(self):
        stmt = upsert_entity(
            indexes=["id"],
            keys_mapping={"id": "id", "updated_at": "updated_at"},
            new_data={"id": "1", "updated_at": func.now()},
            table=self.some_table,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO upsert_model (id, updated_at) VALUES (1, now()) ON CONFLICT (id) DO UPDATE SET updated_at = excluded.updated_at WHERE excluded.updated_at > upsert_model.updated_at"
        )

    def test_upsert_with_list_of_mappings(self):
        stmt = upsert_entity(
            indexes=["id"],
            keys_mapping={"id": "id", "updated_at": "updated_at"},
            new_data=[
                {"id": "1", "updated_at": func.now()},
                {"id": "2", "updated_at": func.now()},
            ],
            table=self.some_table,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO upsert_model (id, updated_at) VALUES (1, now()), (2, now()) ON CONFLICT (id) DO UPDATE SET updated_at = excluded.updated_at WHERE excluded.updated_at > upsert_model.updated_at"
        )

    def test_changes_where_if_refresh_data_is_true(self):
        stmt = upsert_entity(
            indexes=["id"],
            keys_mapping={"id": "id", "updated_at": "updated_at"},
            new_data={"id": "1", "updated_at": func.now()},
            table=self.some_table,
            refresh_data=True,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO upsert_model (id, updated_at) VALUES (1, now()) ON CONFLICT (id) DO UPDATE SET updated_at = excluded.updated_at WHERE excluded.updated_at >= upsert_model.updated_at"
        )

    def test_adds_returning_clause_if_returning_specified(self):
        stmt = upsert_entity(
            indexes=["id"],
            keys_mapping={"id": "id", "updated_at": "updated_at"},
            new_data={"id": "1", "updated_at": func.now()},
            table=self.some_table,
            returning=[self.some_table.c.id],
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO upsert_model (id, updated_at) VALUES (1, now()) ON CONFLICT (id) DO UPDATE SET updated_at = excluded.updated_at WHERE excluded.updated_at > upsert_model.updated_at RETURNING upsert_model.id"
        )

    def test_does_nothing_if_do_nothing_action_was_passed(self):
        stmt = upsert_entity(
            indexes=["id"],
            keys_mapping={"id": "id", "updated_at": "updated_at"},
            new_data={"id": "1", "updated_at": func.now()},
            table=self.some_table,
            action=ConflictAction.DO_NOTHING,
        )
        assert (
            format_statement(stmt)
            == "INSERT INTO upsert_model (id, updated_at) VALUES (1, now()) ON CONFLICT (id) DO NOTHING"
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
