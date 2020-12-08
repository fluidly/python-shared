import base64
import json
from unittest import mock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fluidly.fastapi import dependencies
from fluidly.fastapi.dependencies import get_admin_user, get_authorised_user


@pytest.fixture
def mocked_user_permissions_throws_error(monkeypatch):
    check_user_permissions_mock = mock.MagicMock(return_value=False)
    monkeypatch.delattr(dependencies, "check_user_permissions")
    yield check_user_permissions_mock


@pytest.fixture
def mocked_not_given_permissions(monkeypatch):
    check_user_permissions_mock = mock.MagicMock(return_value=False)
    monkeypatch.setattr(
        dependencies, "check_user_permissions", check_user_permissions_mock
    )
    yield check_user_permissions_mock


@pytest.fixture
def mocked_given_permissions(monkeypatch):
    check_user_permissions_mock = mock.MagicMock(return_value=True)
    monkeypatch.setattr(
        dependencies, "check_user_permissions", check_user_permissions_mock
    )
    yield check_user_permissions_mock


@pytest.fixture
def mocked_permissions_throws_exception(monkeypatch):
    check_admin_permissions_mock = mock.MagicMock(return_value=False)
    monkeypatch.delattr(dependencies, "check_admin_permissions")
    yield check_admin_permissions_mock


@pytest.fixture
def mocked_admin_not_given_permissions(monkeypatch):
    check_admin_permissions_mock = mock.MagicMock(return_value=False)
    monkeypatch.setattr(
        dependencies, "check_admin_permissions", check_admin_permissions_mock
    )
    yield check_admin_permissions_mock


@pytest.fixture
def mocked_admin_given_permissions(monkeypatch):
    check_admin_permissions_mock = mock.MagicMock(return_value=True)
    monkeypatch.setattr(
        dependencies, "check_admin_permissions", check_admin_permissions_mock
    )
    yield check_admin_permissions_mock


class TestAuthBase:
    @staticmethod
    def _encode_claims(claims):
        return base64.b64encode(json.dumps(claims).encode("utf-8")).decode("utf-8")

    @staticmethod
    def _get_dummy_user_info(**kwargs):
        app_metadata = kwargs.get("app_metadata", {})
        internal_metadata = kwargs.get("internal_metadata", {})

        return TestAuthBase._encode_claims(
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

    @pytest.fixture(autouse=True)
    def setup(self):
        fastapi_app = FastAPI()

        @fastapi_app.get("/shared/authorised/{connection_id}")
        def authorised_endpoint(
            connection_id: str, authorised_user=Depends(get_authorised_user)
        ):
            return authorised_user

        @fastapi_app.get("/shared/admin")
        def admin_endpoint(admin_user=Depends(get_admin_user)):
            return admin_user

        self.client = TestClient(fastapi_app)


class TestAuthorised(TestAuthBase):
    def test_user_unauthenticated(self):
        response = self.client.get("/shared/authorised/some:connection_id")
        assert response.status_code == 401
        assert response.json() == {"detail": "User is not authenticated"}

    def test_permissions_unavailable(self):
        response = self.client.get(
            "/shared/authorised/some:connection_id",
            headers={"X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json() == {
            "detail": "An issue occurred while fetching permissions"
        }

    def test_permissions_available_not_granted(self, mocked_not_given_permissions):
        response = self.client.get(
            "/shared/authorised/some:connection_id",
            headers={"X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "User cannot access this resource"}

    def test_permissions_available_granted(self, mocked_given_permissions):
        response = self.client.get(
            "/shared/authorised/some:connection_id",
            headers={
                "X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info(
                    app_metadata={"userId": 2}
                )
            },
        )
        assert response.status_code == 200
        assert response.json() == {"connection_id": "some:connection_id", "user_id": 2}

    def test_service_account_granted(self, mocked_user_permissions_throws_error):
        response = self.client.get(
            "/shared/authorised/some:connection_id",
            headers={
                "X-Endpoint-API-UserInfo": TestAuthorised._get_dummy_user_info(
                    internal_metadata={"isServiceAccount": True}
                )
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "connection_id": "some:connection_id",
            "user_id": None,
        }


class TestAdmin(TestAuthBase):
    def test_admin_unauthenticated(self):
        response = self.client.get("/shared/admin")
        assert response.status_code == 401
        assert response.json() == {"detail": "User is not authenticated"}

    def test_admin_permissions_unavailable(self):
        response = self.client.get(
            "/shared/admin",
            headers={"X-Endpoint-API-UserInfo": TestAdmin._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json() == {
            "detail": "An issue occurred while fetching permissions"
        }

    def test_admin_permissions_available_not_granted(
        self, mocked_admin_not_given_permissions
    ):
        response = self.client.get(
            "/shared/admin",
            headers={"X-Endpoint-API-UserInfo": TestAdmin._get_dummy_user_info()},
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "User cannot access this resource"}

    def test_admin_permissions_available_granted(self, mocked_admin_given_permissions):
        response = self.client.get(
            "/shared/admin",
            headers={
                "X-Endpoint-API-UserInfo": TestAdmin._get_dummy_user_info(
                    app_metadata={"userId": 2}
                )
            },
        )
        assert response.status_code == 200
        assert response.json() == {"user_id": 2}

    def test_admin_service_account_granted(self, mocked_permissions_throws_exception):
        response = self.client.get(
            "/shared/admin",
            headers={
                "X-Endpoint-API-UserInfo": TestAdmin._get_dummy_user_info(
                    internal_metadata={"isServiceAccount": True}
                )
            },
        )
        assert response.status_code == 200
        assert response.json() == {"user_id": None}
