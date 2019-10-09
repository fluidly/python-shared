from unittest import mock

import pytest

from fluidly.flask.api_exception import APIException
from fluidly.structlog import base_logger


@pytest.fixture()
def logger_mock(monkeypatch):
    mock_logger = mock.MagicMock()
    monkeypatch.setattr(base_logger, "get_logger", mock_logger)
    yield mock_logger


def test_rest_log_entrypoint_success(client, logger_mock):
    logger_mock = mock.MagicMock()
    response = client.get("/shared/logging-success")
    assert response.status_code == 200
    import pdb

    assert logger_mock.return_value.info.called


def test_rest_log_entrypoint_exception(client):
    response = client.get("/shared/logging-exception")
    assert response.status_code == 500

