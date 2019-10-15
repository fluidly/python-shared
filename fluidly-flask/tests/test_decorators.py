import base64
import json
from unittest import mock

import pytest
from flask import g
from fluidly.flask import decorators


@pytest.fixture
def mocked_not_given_permissions(monkeypatch):
    check_user_permissions_mock = mock.MagicMock(return_value=False)
    monkeypatch.setattr(
        decorators, "check_user_permissions", check_user_permissions_mock
    )
    yield check_user_permissions_mock


@pytest.fixture
def mocked_given_permissions(monkeypatch):
    check_user_permissions_mock = mock.MagicMock(return_value=True)
    monkeypatch.setattr(
        decorators, "check_user_permissions", check_user_permissions_mock
    )
    yield check_user_permissions_mock


class TestAuthorised:
    @staticmethod
    def _encode_claims(claims):
        return base64.b64encode(json.dumps(claims).encode("utf-8"))

    @staticmethod
    def _get_dummy_user_info(**kwargs):
        app_metadata = kwargs.get("app_metadata", {})
        internal_metadata = kwargs.get("internal_metadata", {})

        return TestAuthorised._encode_claims(
            {
                "claims": json.dumps(
                    {
                        "https://api.fluidly.com/app_metadata": {**app_metadata},
                        "https://api.fluidly.com/internal_metadata": {
                            **internal_metadata
                        },
                    }
                )
            }
        )

    def test_user_unauthenticated(self, client):
        response = client.get("/shared/authorised/some:connection_id")
        assert response.status_code == 401
        assert response.json == {
            "title": "User is not authenticated",
            "status": 401,
            "detail": None,
        }

    def test_permissions_unavailable(self, client):
        response = client.get(
            "/shared/authorised/some:connection_id",
            headers={"X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json == {
            "title": "An issue occurred while fetching permissions",
            "status": 403,
            "detail": None,
        }

    def test_permissions_available_not_granted(
        self, client, mocked_not_given_permissions
    ):
        response = client.get(
            "/shared/authorised/some:connection_id",
            headers={"X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json == {
            "title": "User cannot access this resource",
            "status": 403,
            "detail": None,
        }

    def test_permissions_available_granted(
        self, client, flask_app, mocked_given_permissions
    ):
        response = client.get(
            "/shared/authorised/some:connection_id",
            headers={
                "X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info(
                    app_metadata={"userId": 2}
                )
            },
        )
        assert response.status_code == 200
        assert response.data == b"some:connection_id"

        assert g.connection_id == "some:connection_id"
        assert g.user_id == 2

    def test_service_account_granted(self, client, mocked_not_given_permissions):
        response = client.get(
            "/shared/authorised/some:connection_id",
            headers={
                "X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info(
                    internal_metadata={"isServiceAccount": True}
                )
            },
        )
        assert response.status_code == 200
        assert response.data == b"some:connection_id"

        assert g.connection_id == "some:connection_id"
        assert g.user_id == None