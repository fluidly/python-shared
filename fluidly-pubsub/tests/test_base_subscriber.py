from unittest import mock

from fluidly.pubsub.base_subscriber import setup_base_subscriber


def test_setup_base_subscriber():
    mock_subscriber = mock.MagicMock()
    mock_subscription_name = mock.Mock()
    mock_callback = mock.MagicMock()
    path_mock = mock.MagicMock()

    mock_subscriber.subscription_path = mock.MagicMock(return_value=path_mock)
    mock_subscriber.subscribe = mock.MagicMock()

    subscriptions = [(mock_subscription_name, mock_callback)]

    setup_base_subscriber(mock_subscriber, subscriptions)

    result = mock_subscriber.subscribe.call_args_list[0]

    assert result[0][0] == path_mock
    assert result[1]["callback"] == mock_callback
