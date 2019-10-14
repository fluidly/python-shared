from unittest import mock

import pytest

import responses
from fluidly.auth import jwt_requests
from fluidly.auth.jwt_requests import make_jwt_request


@pytest.fixture()
def mocked_requests(monkeypatch):
    mock_requests = mock.MagicMock()
    monkeypatch.setattr(jwt_requests, "requests", mock_requests)
    yield mock_requests


class TestMakeJWTRequests:
    JWT = b"test"
    URL = "https://test.url"

    def test_making_signed_call(self, mocked_responses):
        mocked_responses.add(responses.GET, TestMakeJWTRequests.URL)

        response = make_jwt_request(TestMakeJWTRequests.JWT, TestMakeJWTRequests.URL)

        assert response.status_code == 200

    def test_passing_jwt(self, mocked_requests):
        make_jwt_request(TestMakeJWTRequests.JWT, TestMakeJWTRequests.URL)

        mocked_requests.get.assert_called_with(
            "https://test.url",
            headers={"Authorization": "Bearer test", "content-type": "text/html"},
        )
