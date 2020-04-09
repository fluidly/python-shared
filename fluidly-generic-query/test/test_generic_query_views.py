import json
from unittest.mock import MagicMock, Mock

import pytest

from fluidly.generic_query import generic_query_views


class MockColumn:
    def __init__(self, name):
        self.name = name


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


@pytest.fixture()
def mock_columns(mocked_inspect, monkeypatch):
    def func(columns):
        insights_mock = Mock()
        mocked_inspect.return_value = insights_mock
        insights_mock.columns = []
        insights_mock.columns = [MockColumn(column) for column in columns]
        mock_db_session = MagicMock()
        monkeypatch.setattr(generic_query_views, "db_session", mock_db_session)
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_db_session.return_value = mock_session

    return func


def test_generic_query_model_not_found(client):
    model = "not_a_table"

    args = {"model": model}
    result = client.post("/debug/connection-views", data=json.dumps(args))

    assert result.status_code == 404


def test_generic_query_invalid_json(client):
    model = "mock_model"

    result = client.post(f"/debug/connection-views/{model}", data="segedrh{{{")

    assert result.status_code == 422


def test_generic_query_columns_not_found(client, mock_columns):
    model = "mock_model"

    args = {"query": {"id": "id_value", "some_random_column": "erwerwer9"}}
    mock_columns([])

    result = client.post(f"/debug/connection-views/{model}", json=args)

    assert result.status_code == 400


def test_generic_query_does_not_include_connection_id(client, mock_columns):
    model = "mock_model"

    args = {"query": {"id": "id_value"}}

    mock_columns("id")

    result = client.post(f"/debug/connection-views/{model}", json=args)

    assert result.status_code == 400


def test_generic_query_invalid_page_number(client, mock_columns):
    model = "mock_model"

    args = {"query": {"id": "id_value", "due_date": "2019-12-09"}, "page": 0}
    mock_columns(["id", "due_date"])

    result = client.post(f"/debug/connection-views/{model}", json=args)

    assert result.status_code == 400


def test_generic_query_returns_query_in_meta(client, mock_columns):
    model = "mock_model"

    args = {
        "query": {"connectionId": "idValue", "dueDate": "2019-12-09"},
        "page": 1,
        "pageSize": 5,
    }

    mock_columns(["connection_id", "due_date"])

    result = client.post(f"/debug/connection-views/{model}", json=args)
    assert result.status_code == 200
    meta = result.json["meta"]
    assert "dueDate" in meta["query"]
