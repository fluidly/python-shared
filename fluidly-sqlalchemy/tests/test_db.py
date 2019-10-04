from unittest import mock

import pytest
from fluidly.sqlalchemy import db
from fluidly.sqlalchemy.db import db_session
from pytest import raises


@pytest.fixture()
def sessionmaker_mock(monkeypatch):
    mock_sessionmaker = mock.MagicMock()
    monkeypatch.setattr(db, "sessionmaker", mock_sessionmaker)
    yield mock_sessionmaker


def test_db_session(sessionmaker_mock):

    session_mock = mock.MagicMock()

    sessionmaker_mock.return_value = session_mock

    with db_session() as session:
        yield

    assert session_mock.close.called


def test_db_session_with_exception(sessionmaker_mock):

    session_mock = mock.MagicMock()

    sessionmaker_mock.side_effect = Exception("Random exception")

    with raises(Exception, message="Random exception"):
        with db_session() as session:
            yield

    assert session_mock.rollback.called
