from unittest import mock

from fluidly.sqlalchemy.upsert import get_on_conflict_stmt, update_required


def test_get_on_conflict_stmt():
    stmt = mock.MagicMock()
    index = mock.MagicMock()
    where = mock.MagicMock()

    stmt.excluded.argument = "Test"
    stmt.excluded.another_argument = "Test"

    get_on_conflict_stmt(stmt, index, ["argument", "another_argument"], where)

    args_list = stmt.on_conflict_do_update.call_args_list

    assert stmt.on_conflict_do_update.called
    assert args_list[0][1]["index_elements"] == index
    assert args_list[0][1]["set_"]["argument"] == "Test"
    assert args_list[0][1]["where"] == where


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
