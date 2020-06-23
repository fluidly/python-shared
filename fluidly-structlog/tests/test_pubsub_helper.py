from unittest import mock
from unittest.mock import MagicMock

import pytest

from fluidly.structlog import pubsub_helper
from fluidly.structlog.pubsub_helper import pubsub_log_entrypoint_class

mock_message = MagicMock(attributes={})


@pytest.fixture()
def mock_structlog(monkeypatch):
    get_logger_mock = mock.Mock()
    monkeypatch.setattr(pubsub_helper, "get_logger", get_logger_mock)
    return get_logger_mock.return_value.new.return_value


def test_pubsub_log_entrypoint(mock_structlog):
    class TestClass:
        @pubsub_log_entrypoint_class
        def test_func(self, session, organisation):
            pass

    TestClass().test_func("session", mock_message)
    assert mock_structlog.info.called


def test_pubsub_log_entrypoint_on_error(mock_structlog):
    class TestClass:
        @pubsub_log_entrypoint_class
        def test_func(self, session, organisation):
            raise RuntimeError

    throws_error = False
    try:
        TestClass().test_func("session", mock_message)
    except RuntimeError:
        throws_error = True
    assert throws_error
    assert mock_structlog.error.called
    args = mock_structlog.error.call_args
    assert args[1].pop("message_age")
