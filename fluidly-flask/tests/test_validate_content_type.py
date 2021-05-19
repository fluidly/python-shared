from unittest import mock

import pytest
from flask import Response, request

from fluidly.flask import validate_content_type as module
from fluidly.flask.validate_content_type import validate_content_type


@pytest.fixture()
def logger_mock(monkeypatch):
    mock_logger = mock.MagicMock()
    monkeypatch.setattr(module, "get_logger", lambda: mock_logger)
    yield mock_logger


@pytest.fixture()
def request_mock(monkeypatch, request_context):
    mock_request = mock.create_autospec(request)
    mock_request.view_args = {}
    mock_request.full_path = "/foo"
    monkeypatch.setattr(module, "request", mock_request)
    yield mock_request


@pytest.fixture()
def request_mock_with_no_view_args(request_mock):
    request_mock.view_args = None
    yield request_mock


def test_content_type_valid(logger_mock, request_mock):
    request_mock.headers = {"Accept": "text/plain"}

    response = Response("foobar", content_type="text/plain")

    validated_response = validate_content_type(response)

    assert validated_response == response
    assert not logger_mock.warning.called


def test_content_type_invalid(logger_mock, request_mock):
    request_mock.headers = {"Accept": "text/plain"}

    response = Response("{}", content_type="application/json")

    validated_response = validate_content_type(response)

    assert validated_response == response
    assert logger_mock.warning.called
    logger_mock.warning.assert_called_with(
        "Incompatible request Accept header and response content-type",
        args={},
        headers=request_mock.headers,
        url="/foo",
        request_accept_header="text/plain",
        response_content_type="application/json",
    )


def test_no_accept_header(logger_mock, request_mock):
    request_mock.headers = {}

    response = Response("{}", content_type="application/json")

    validated_response = validate_content_type(response)

    assert validated_response == response
    assert not logger_mock.warning.called


def test_wildcard_accept_header(logger_mock, request_mock):
    request_mock.headers = {"Accept": "*/*"}

    response = Response("{}", content_type="application/json")

    validated_response = validate_content_type(response)

    assert validated_response == response
    assert not logger_mock.warning.called


def test_multiple_accept_types_valid(logger_mock, request_mock):
    request_mock.headers = {"Accept": "application/json,application/text"}

    response = Response("{}", content_type="application/json")

    validate_content_type(response)
    assert not logger_mock.warning.called


def test_multiple_accept_types_invalid(logger_mock, request_mock):
    request_mock.headers = {"Accept": "application/json,application/text"}

    response = Response("foobar", content_type="text/plain")

    validate_content_type(response)
    assert logger_mock.warning.called


def test_multiple_accept_types_with_wildcard(logger_mock, request_mock):
    request_mock.headers = {"Accept": "application/json,*/*"}

    response = Response("foobar", content_type="text/plain")

    validate_content_type(response)
    assert not logger_mock.warning.called


def test_subset_content_type(logger_mock, request_mock):
    request_mock.headers = {"Accept": "application/json"}

    response = Response("foobar", content_type="application/problem+json")

    validate_content_type(response)
    assert not logger_mock.warning.called


def test_invalid_request_with_no_view_args(logger_mock, request_mock_with_no_view_args):
    request_mock_with_no_view_args.headers = {"Accept": "text/plain"}

    response = Response("{}", content_type="application/json")

    validate_content_type(response)
    assert logger_mock.warning.called

    args, kwargs = logger_mock.warning.call_args
    assert kwargs["args"] is None
