from unittest import mock
from unittest.mock import MagicMock

import pytest
from fluidly.pubsub import base_generate_callback
from fluidly.pubsub.base_generate_callback import setup_base_generate_callback
from fluidly.pubsub.exceptions import DropMessageException
from sqlalchemy.exc import IntegrityError


@pytest.fixture()
def mock_message_class(monkeypatch):
    monkeypatch.setattr(base_generate_callback, "APPLICATION_NAME", "python-shared")


@pytest.fixture()
def mock_message_handler():
    message_handler = mock.MagicMock()
    return message_handler


def test_base_generate_callback_wrong_audience(
    mock_message_class, mock_message_handler
):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "random_service",
        }
    )
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert not mock_message_handler.called
    assert mock_message.ack.called


def test_base_generate_callback_correct_audience(
    mock_message_class, mock_message_handler
):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "python-shared",
        }
    )
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_base_generate_callback_no_audience(mock_message_handler):
    mock_message = MagicMock(
        attributes={"connection_id": "qbo:123", "fluidlyWebOrganisationId": "12"}
    )
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_base_generate_callback_empty_audience(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_base_generate_callback_drop_message_exception(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )

    mock_message_handler.side_effect = DropMessageException("mocked error")
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message.ack.called


def test_base_generate_callback_integrity_error(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )

    mock_message_handler.side_effect = IntegrityError("statement", "params", "orig")
    callback = setup_base_generate_callback(MagicMock(), mock_message_handler)

    with pytest.raises(IntegrityError) as exception:
        callback(mock_message)

    assert mock_message.ack.called
