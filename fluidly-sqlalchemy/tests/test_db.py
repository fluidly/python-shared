from unittest import mock

import pytest
from pytest import raises

from fluidly.sqlalchemy import db
from fluidly.sqlalchemy.db import db_session


@pytest.fixture()
def sessionmaker_mock(monkeypatch):
    mock_sessionmaker = mock.MagicMock()
    monkeypatch.setattr(db, "SessionMaker", mock_sessionmaker)
    yield mock_sessionmaker


def test_db_session(sessionmaker_mock):

    session_mock = mock.MagicMock()

    sessionmaker_mock.return_value = session_mock

    with db_session():
        pass

    assert session_mock.close.called


def test_db_session_with_exception(sessionmaker_mock):

    session_mock = mock.MagicMock()

    sessionmaker_mock.return_value = session_mock

    with raises(Exception, match="Random exception"):
        with db_session():
            raise Exception("Random exception")

    assert session_mock.rollback.called
