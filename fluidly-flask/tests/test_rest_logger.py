from unittest import mock

import pytest
from fluidly.structlog import base_logger


@pytest.fixture()
def logger_mock(monkeypatch):
    mock_logger = mock.MagicMock()
    monkeypatch.setattr(base_logger, "get_logger", lambda: mock_logger)
    yield mock_logger


def test_rest_log_entrypoint_success(client, logger_mock):
    response = client.get("/shared/logging-success")
    assert response.status_code == 200

    assert logger_mock.new.called
    assert logger_mock.new.return_value.info.called


def test_rest_log_entrypoint_exception(client, logger_mock):
    response = client.get("/shared/logging-exception")
    assert response.status_code == 500

    assert logger_mock.new.called
    assert logger_mock.new.return_value.error.called
