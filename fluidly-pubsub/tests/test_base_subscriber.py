from unittest import mock
from unittest.mock import MagicMock

import pytest
from fluidly.pubsub import base_subscriber
from fluidly.pubsub.base_subscriber import generate_callback, setup_base_subscriber
from fluidly.pubsub.exceptions import DropMessageException
from sqlalchemy.exc import IntegrityError


@pytest.fixture()
def mock_message_class(monkeypatch):
    monkeypatch.setattr(base_subscriber, "APPLICATION_NAME", "python-shared")


@pytest.fixture()
def mock_message_handler():
    message_handler = mock.MagicMock()
    return message_handler


def test_generate_callback_wrong_audience(mock_message_class, mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "random_service",
        }
    )
    callback = generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert not mock_message_handler.called
    assert mock_message.ack.called


def test_generate_callback_correct_audience(mock_message_class, mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "python-shared",
        }
    )
    callback = generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_generate_callback_no_audience(mock_message_handler):
    mock_message = MagicMock(
        attributes={"connection_id": "qbo:123", "fluidlyWebOrganisationId": "12"}
    )
    callback = generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_generate_callback_empty_audience(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )
    callback = generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message_handler.called


def test_generate_callback_drop_message_exception(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )

    mock_message_handler.side_effect = DropMessageException("mocked error")
    callback = generate_callback(MagicMock(), mock_message_handler)

    callback(mock_message)

    assert mock_message.ack.called


def test_generate_callback_integrity_error(mock_message_handler):
    mock_message = MagicMock(
        attributes={
            "connection_id": "qbo:123",
            "fluidlyWebOrganisationId": "12",
            "audience": "",
        }
    )

    mock_message_handler.side_effect = IntegrityError("statement", "params", "orig")
    callback = generate_callback(MagicMock(), mock_message_handler)

    with pytest.raises(IntegrityError) as exception:
        callback(mock_message)

    assert mock_message.ack.called


def test_setup_base_subscriber(monkeypatch):
    mock_gen_callback = mock.MagicMock()
    mock_callback = mock.MagicMock()
    mock_callback.return_value = mock_gen_callback
    monkeypatch.setattr(base_subscriber, "generate_callback", mock_callback)

    mock_subscriber = mock.MagicMock()
    mock_subscription_name = mock.Mock()
    path_mock = mock.MagicMock()

    mock_subscriber.subscription_path = mock.MagicMock(return_value=path_mock)
    mock_subscriber.subscribe = mock.MagicMock()

    subscriptions = [(mock_subscription_name, mock_callback)]

    setup_base_subscriber(mock_subscriber, subscriptions)

    result = mock_subscriber.subscribe.call_args_list[0]

    assert result[0][0] == path_mock
    assert result[1]["callback"] == mock_gen_callback
