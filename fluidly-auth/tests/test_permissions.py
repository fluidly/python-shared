import re
from unittest import mock

import pytest
import responses

from fluidly.auth import permissions
from fluidly.auth.permissions import (
    UserPermissionsPayloadException,
    check_admin_permissions,
    check_user_permissions,
)

FLUIDLY_API_URL = "https://fluidly-api.url"


@pytest.fixture()
def mocked_generate_jwt(monkeypatch):
    mock_generate_jwt = mock.MagicMock()
    monkeypatch.setattr(permissions, "generate_jwt", mock_generate_jwt)
    yield mock_generate_jwt


@pytest.fixture()
def mocked_200_granted_permissions(mocked_responses):
    mocked_responses.add(
        responses.GET,
        re.compile(f"{FLUIDLY_API_URL}/*"),
        json={"grantAccess": True},
        status=200,
    )

    yield mocked_responses


@pytest.fixture()
def mocked_200_not_granted_permissions(mocked_responses):
    mocked_responses.add(
        responses.GET,
        re.compile(f"{FLUIDLY_API_URL}/*"),
        json={"grantAccess": False, "reason": "Being impolite"},
        status=200,
    )

    yield mocked_responses


@pytest.fixture()
def mocked_500_permissions(mocked_responses):
    mocked_responses.add(responses.GET, re.compile(f"{FLUIDLY_API_URL}/*"), status=500)

    yield mocked_responses


@pytest.fixture()
def mocked_env_permissions_url_path(monkeypatch):
    mock_env_permissions_url = mock.MagicMock()
    mock_env_permissions_url.return_value = FLUIDLY_API_URL
    monkeypatch.setattr(permissions.os, "getenv", mock_env_permissions_url)
    yield mock_env_permissions_url


class TestCheckUserPermissions:
    def test_required_permission_url(self):
        with pytest.raises(ValueError, match="Please provide FLUIDLY_API_URL"):
            check_user_permissions({}, "connection_id")

    def test_passing_env_permission_url(
        self,
        mocked_generate_jwt,
        mocked_200_granted_permissions,
        mocked_env_permissions_url_path,
    ):
        try:
            check_user_permissions({}, "connection_id")
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_using_kwargs_permission_url(
        self, mocked_generate_jwt, mocked_200_granted_permissions
    ):
        try:
            check_user_permissions({}, "connection_id", fluidly_api_url=FLUIDLY_API_URL)
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_payload_exception_when_unavailable(
        self, mocked_generate_jwt, mocked_500_permissions
    ):
        with pytest.raises(UserPermissionsPayloadException):
            check_user_permissions({}, "connection_id", fluidly_api_url=FLUIDLY_API_URL)

    def test_not_granted_permissions(
        self, mocked_generate_jwt, mocked_200_not_granted_permissions
    ):
        assert (
            check_user_permissions({}, "connection_id", fluidly_api_url=FLUIDLY_API_URL)
            == False
        )

    def test_granted_permissions(
        self, mocked_generate_jwt, mocked_200_granted_permissions
    ):
        assert (
            check_user_permissions({}, "connection_id", fluidly_api_url=FLUIDLY_API_URL)
            == True
        )


class TestCheckAdminPermissions:
    def test_admin_required_permission_url(self):
        with pytest.raises(ValueError, match="Please provide FLUIDLY_API_URL"):
            check_admin_permissions({})

    def test_admin_passing_env_permission_url(
        self,
        mocked_generate_jwt,
        mocked_200_granted_permissions,
        mocked_env_permissions_url_path,
    ):
        try:
            check_admin_permissions({})
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_admin_using_kwargs_permission_url(
        self, mocked_generate_jwt, mocked_200_granted_permissions
    ):
        try:
            check_admin_permissions({}, fluidly_api_url=FLUIDLY_API_URL)
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_admin_payload_exception_when_unavailable(
        self, mocked_generate_jwt, mocked_500_permissions
    ):
        with pytest.raises(UserPermissionsPayloadException):
            check_admin_permissions({}, fluidly_api_url=FLUIDLY_API_URL)

    def test_admin_not_granted_permissions(
        self, mocked_generate_jwt, mocked_200_not_granted_permissions
    ):
        assert check_admin_permissions({}, fluidly_api_url=FLUIDLY_API_URL) == False

    def test_admin_granted_permissions(
        self, mocked_generate_jwt, mocked_200_granted_permissions
    ):
        assert check_admin_permissions({}, fluidly_api_url=FLUIDLY_API_URL) == True
