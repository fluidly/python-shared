from unittest import mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from fluidly.fastapi import middleware
from fluidly.fastapi.middleware import LoggingMiddleware


def default_test_route():
    return {"msg": "Sending hugs from FastAPI"}


@pytest.fixture()
def mock_structlog(monkeypatch):
    get_logger_mock = mock.Mock()
    monkeypatch.setattr(middleware, "get_logger", get_logger_mock)
    return get_logger_mock.return_value


@pytest.fixture()
def setup_fastapi():
    def _fastapi_app(
        route=default_test_route, route_path="/test", custom_middlewares=None
    ):
        custom_middlewares = custom_middlewares or []

        fastapi_app = FastAPI()
        fastapi_app.add_api_route(route_path, route)

        for custom_middleware in custom_middlewares:
            fastapi_app.add_middleware(custom_middleware)

        return TestClient(fastapi_app)

    return _fastapi_app


class TestLoggingMiddleware:
    def test_logs_message_on_successful_request(self, setup_fastapi, mock_structlog):
        client = setup_fastapi(custom_middlewares=[LoggingMiddleware])

        client.get("/test").json()

        assert mock_structlog.info.called
        args, kwargs = mock_structlog.info.call_args

        assert args == ("rest_request_processed",)
        assert kwargs["status_code"] == 200
        assert kwargs["success"] == True

    def test_binds_request_data_on_successful_request(
        self, setup_fastapi, mock_structlog
    ):
        def route(partner_id: int, connection_id: str):
            return

        client = setup_fastapi(
            route=route,
            route_path="/{partner_id}/{connection_id}",
            custom_middlewares=[LoggingMiddleware],
        )

        client.get("/1/xero:123").json()

        assert mock_structlog.bind.called
        args, kwargs = mock_structlog.bind.call_args

        assert kwargs["args"] == {"partner_id": "1", "connection_id": "xero:123"}
        assert kwargs["partner_id"] == "1"
        assert kwargs["connection_id"] == "xero:123"
        assert kwargs["url"] == "http://testserver/1/xero:123"
        assert (
            kwargs["callback"]
            == "TestLoggingMiddleware.test_binds_request_data_on_successful_request.<locals>.route"
        )
        assert kwargs["headers"] == {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        }

    def test_logs_message_on_explicit_http_exception(
        self, setup_fastapi, mock_structlog
    ):
        def route():
            raise HTTPException(status_code=404, detail="Test not found")

        client = setup_fastapi(route=route, custom_middlewares=[LoggingMiddleware])
        client.get("/test")

        assert mock_structlog.info.called == False, "logger.info was called"

        assert mock_structlog.error.called
        args, kwargs = mock_structlog.error.call_args

        assert args == ("rest_request_processed",)
        assert kwargs["status_code"] == 404
        assert kwargs["success"] == False

    def test_returns_json_problem_on_explicit_http_exception(
        self, setup_fastapi, mock_structlog
    ):
        def route():
            raise HTTPException(status_code=404, detail="Test not found")

        client = setup_fastapi(route=route, custom_middlewares=[LoggingMiddleware])

        json_response = client.get("/test")

        assert json_response.json() == {"detail": "Test not found"}
        assert json_response.headers["content-type"] == "application/json+problem"

    def test_binds_request_data_on_explicit_http_exception(
        self, setup_fastapi, mock_structlog
    ):
        def route(partner_id: int, connection_id: str):
            raise HTTPException(status_code=404, detail="Test not found")

        client = setup_fastapi(
            route=route,
            route_path="/{partner_id}/{connection_id}",
            custom_middlewares=[LoggingMiddleware],
        )

        client.get("/1/xero:123").json()

        assert mock_structlog.bind.called
        args, kwargs = mock_structlog.bind.call_args

        assert kwargs["args"] == {"partner_id": "1", "connection_id": "xero:123"}
        assert kwargs["partner_id"] == "1"
        assert kwargs["connection_id"] == "xero:123"
        assert kwargs["url"] == "http://testserver/1/xero:123"
        assert (
            kwargs["callback"]
            == "TestLoggingMiddleware.test_binds_request_data_on_explicit_http_exception.<locals>.route"
        )
        assert kwargs["headers"] == {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        }

    def test_logs_message_on_unexpected_exception(self, setup_fastapi, mock_structlog):
        def route():
            1 / 0

        client = setup_fastapi(route=route, custom_middlewares=[LoggingMiddleware])
        client.get("/test")

        assert mock_structlog.info.called == False, "logger.info was called"

        assert mock_structlog.error.called
        args, kwargs = mock_structlog.error.call_args

        assert args == ("rest_request_processed",)
        assert kwargs["status_code"] == 500
        assert kwargs["success"] == False

    def test_returns_json_problem_on_unexpected_exception(
        self, setup_fastapi, mock_structlog
    ):
        def route():
            1 / 0

        client = setup_fastapi(route=route, custom_middlewares=[LoggingMiddleware])

        json_response = client.get("/test")

        assert json_response.json() == {"detail": "An unknown error occurred"}
        assert json_response.headers["content-type"] == "application/json+problem"

    def test_binds_request_data_on_unexpected_exception(
        self, setup_fastapi, mock_structlog
    ):
        def route(partner_id: int, connection_id: str):
            1 / 0

        client = setup_fastapi(
            route=route,
            route_path="/{partner_id}/{connection_id}",
            custom_middlewares=[LoggingMiddleware],
        )

        client.get("/1/xero:123").json()

        assert mock_structlog.bind.called
        args, kwargs = mock_structlog.bind.call_args

        assert kwargs["args"] == {"partner_id": "1", "connection_id": "xero:123"}
        assert kwargs["partner_id"] == "1"
        assert kwargs["connection_id"] == "xero:123"
        assert kwargs["url"] == "http://testserver/1/xero:123"
        assert (
            kwargs["callback"]
            == "TestLoggingMiddleware.test_binds_request_data_on_unexpected_exception.<locals>.route"
        )
        assert kwargs["headers"] == {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        }
