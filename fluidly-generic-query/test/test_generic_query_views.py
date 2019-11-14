from unittest.mock import MagicMock, Mock
from json import JSONDecodeError

import pytest
from fluidly.generic_query import generic_query_views
from fluidly.generic_query.generic_query_views import post_model_by_connection_id_query
from fluidly.generic_query.mock_model_factory import MockModel, mock_model_factory
from fluidly.sqlalchemy.db import db_session
from pytest import raises
from fluidly.sqlalchemy import db

from fluidly.flask.api_exception import APIException


class MockColumn:
    def __init__(self, name):
        self.name = name

@pytest.fixture()
def mock_base():
    base_mock = Mock()
    values_mock = [MockModel()]

    base_mock._decl_class_registry.values.return_value = values_mock

    return base_mock


@pytest.fixture()
def mocked_request(monkeypatch):
    request_mock = MagicMock()
    monkeypatch.setattr(generic_query_views, "request", request_mock)
    yield request_mock


@pytest.fixture()
def mocked_inspect(monkeypatch):
    inspect_mock = MagicMock()
    monkeypatch.setattr(generic_query_views, "inspect", inspect_mock)
    yield inspect_mock


def test_post_model_by_connection_id_query_model_not_found(mock_base):
    model = "not_a_table"

    result = post_model_by_connection_id_query(mock_base, model)

    assert result.status_code == 404


def test_post_model_by_connection_id_query_invalid_json(mocked_request, mock_base):
    model = "mock_model"

    mocked_request.get_json.side_effect = JSONDecodeError("", "", 0)

    with raises(APIException):
        result = post_model_by_connection_id_query(mock_base, model)

        assert result.status_code == 422


def test_post_model_by_connection_id_query_wrong_columns(mocked_request, mock_base, mocked_inspect):
    model = "mock_model"
    insights_mock = Mock()

    mocked_request.get_json.return_value = {"query": {"id": "id_value", "some_random_column": "erwerwer9"}}
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = []

    result = post_model_by_connection_id_query(mock_base, model)

    assert result.status_code == 400


def test_post_model_by_connection_id_query_wrong_page(mocked_request, mock_base, mocked_inspect):
    model = "mock_model"
    insights_mock = Mock()

    mocked_request.get_json.return_value = {"query": {"id": "id_value", "due_date": "2019-12-09"}, "page": 0}
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = [MockColumn("id"), MockColumn("due_date")]

    result = post_model_by_connection_id_query(mock_base, model)

    assert result.status_code == 400


def test_post_model_by_connection_id_query_proper_document_query(monkeypatch, mocked_request, mock_base, mocked_inspect):
    model = "mock_model"
    insights_mock = Mock()

    mocked_request.get_json.return_value = {"query": {"id": "id_value", "due_date": "2019-12-09"}, "page": 1, "page_size": 5}
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = [MockColumn("id"), MockColumn("due_date")]

    mock_db_session = MagicMock()
    monkeypatch.setattr(generic_query_views, "db_session", mock_db_session)
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_db_session.return_value = mock_session

    result = post_model_by_connection_id_query(mock_base, model)
    assert result.status_code == 200
