from unittest import mock

import pytest

from fluidly.pubsub import base_subscriber
from fluidly.pubsub.base_subscriber import setup_base_subscriber


@pytest.fixture
def subscriber_mock(monkeypatch):
    mock_subscriber = mock.MagicMock()
    monkeypatch.setattr(base_subscriber, "subscriber", mock_subscriber)
    yield mock_subscriber


def test_setup_base_subscriber(subscriber_mock):
    mock_subscription_name = mock.Mock()
    mock_callback = mock.Mock()
    path_mock = mock.MagicMock()
    subscriber_mock.subscription_path = mock.MagicMock(return_value=path_mock)

    subscriptions = [(mock_subscription_name, mock_callback)]

    setup_base_subscriber(subscriptions)

    result = subscriber_mock.subscribe.call_args_list[0]

    assert result[0][0] == path_mock
    assert result[1]["callback"] == mock_callback
