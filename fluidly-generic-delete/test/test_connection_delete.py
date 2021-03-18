from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy import Column, MetaData, String, Table

from fluidly.generic_delete.connection_delete import DeleteConnectionConsumer
from fluidly.pubsub.message import Message
from fluidly.pubsub.tests import message_from_dict


@pytest.fixture
def mock_session():
    return MagicMock()


def mock_message(payload: str, attributes: dict = None):
    pubsub_message = mock.Mock()
    pubsub_message.data = payload
    pubsub_message.attributes = attributes

    return Message(pubsub_message)


def test_delete_by_connection_id_when_table_valid(mock_session):
    base_mock = Mock()
    metadata_mock = Mock()
    tables_mock = Mock()

    table_mock = Table(
        "foo", MetaData(), Column("connection_id", String(), primary_key=True)
    )

    base_mock.metadata = metadata_mock
    metadata_mock.tables = tables_mock
    tables_mock.values.return_value = [table_mock]

    consumer = DeleteConnectionConsumer(base_mock)
    delete_message = message_from_dict({"connection_id": "test:123"})

    consumer.delete_by_connection_id(mock_session, delete_message, False)

    assert mock_session.execute.called
    assert mock_session.commit.called


def test_delete_by_connection_id_when_table_invalid(mock_session):
    base_mock = Mock()
    metadata_mock = Mock()
    tables_mock = Mock()

    table_mock = Mock()
    columns = Mock()

    table_mock.c = columns
    columns.get.side_effect = lambda c: None

    base_mock.metadata = metadata_mock
    metadata_mock.tables = tables_mock
    tables_mock.values.return_value = [table_mock]

    consumer = DeleteConnectionConsumer(base_mock)
    delete_message = message_from_dict({"connection_id": "test:123"})

    consumer.delete_by_connection_id(mock_session, delete_message, False)

    assert not mock_session.execute.called
    assert mock_session.commit.called


def test_delete_ignores_ignored_tables(mock_session):
    base_mock = Mock()
    metadata_mock = Mock()
    tables_mock = Mock()

    table_mock = Mock()
    columns = Mock()

    table_mock.c = columns
    table_mock.name = "ignore"
    columns.get.side_effect = lambda c: None

    base_mock.metadata = metadata_mock
    metadata_mock.tables = tables_mock
    tables_mock.values.return_value = [table_mock]

    consumer = DeleteConnectionConsumer(base_mock, ["ignore"])
    delete_message = message_from_dict({"connection_id": "test:123"})

    consumer.delete_by_connection_id(mock_session, delete_message, False)

    assert not mock_session.execute.called
    assert mock_session.commit.called
