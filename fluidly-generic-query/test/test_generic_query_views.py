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


def test_post_model_by_connection_id_query_model_not_found(client):
    model = "not_a_table"

    args = {"model": model}
    result = client.post("/debug/connection-views", data=json.dumps(args))

    assert result.status_code == 404


def test_post_model_by_connection_id_query_invalid_json(client):
    model = "mock_model"

    result = client.post(f"/debug/connection-views/{model}", data="segedrh{{{")

    assert result.status_code == 422


def test_post_model_by_connection_id_query_wrong_columns(client, mocked_inspect):
    model = "mock_model"
    insights_mock = Mock()

    args = {"query": {"id": "id_value", "some_random_column": "erwerwer9"}}
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = []

    result = client.post(f"/debug/connection-views/{model}", json=args)

    assert result.status_code == 400


def test_post_model_by_connection_id_query_wrong_page(mocked_inspect, client):
    model = "mock_model"
    insights_mock = Mock()

    args = {"query": {"id": "id_value", "due_date": "2019-12-09"}, "page": 0}
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = [MockColumn("id"), MockColumn("due_date")]

    result = client.post(f"/debug/connection-views/{model}", json=args)

    assert result.status_code == 400


def test_post_model_by_connection_id_query_proper_document_query(
    monkeypatch, mocked_inspect, client
):
    model = "mock_model"
    insights_mock = Mock()

    args = {
        "query": {"id": "id_value", "due_date": "2019-12-09"},
        "page": 1,
        "pageSize": 5,
    }
    mocked_inspect.return_value = insights_mock
    insights_mock.columns = [MockColumn("id"), MockColumn("due_date")]

    mock_db_session = MagicMock()
    monkeypatch.setattr(generic_query_views, "db_session", mock_db_session)
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_db_session.return_value = mock_session

    result = client.post(f"/debug/connection-views/{model}", json=args)
    assert result.status_code == 200
