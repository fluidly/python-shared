from unittest import mock

import pytest
from freezegun import freeze_time

from fluidly.auth import jwt
from fluidly.auth.jwt import generate_jwt


@pytest.fixture()
def mocked_google_credentials(monkeypatch):
    mock_credentials = mock.MagicMock()
    mock_credentials.from_service_account_file.return_value.service_account_email = (
        "test@email.com"
    )
    monkeypatch.setattr(jwt, "Credentials", mock_credentials)
    yield mock_credentials


@pytest.fixture()
def mocked_crypt(monkeypatch):
    mock_crypt = mock.MagicMock()
    monkeypatch.setattr(jwt, "crypt", mock_crypt)
    yield mock_crypt


@pytest.fixture()
def mocked_jwt(monkeypatch):
    mock_jwt = mock.MagicMock()
    mock_jwt.encode.return_value = b"JWT_TOKEN"
    monkeypatch.setattr(jwt, "jwt", mock_jwt)
    yield mock_jwt


@pytest.fixture()
def mocked_env_credentials_path(monkeypatch):
    mock_env_credentials = mock.MagicMock()

    def load_env_var(env_name):
        if env_name == "GOOGLE_APPLICATION_CREDENTIALS":
            return "/some/path/credentials.json"
        return None

    mock_env_credentials.side_effect = load_env_var
    monkeypatch.setattr(jwt.os, "getenv", mock_env_credentials)
    yield mock_env_credentials


@pytest.fixture()
def mocked_auth0_jwt_token(monkeypatch):
    mock_env_credentials = mock.MagicMock()

    def load_env_var(env_name):
        if env_name == "AUTH0_JWT_TOKEN":
            return b"AUTH0_JWT_TOKEN"
        return None

    mock_env_credentials.side_effect = load_env_var
    monkeypatch.setattr(jwt.os, "getenv", mock_env_credentials)
    yield mock_env_credentials


class TestGenerateJWT:
    def test_required_credentials(self):
        with pytest.raises(
            ValueError, match="Please provide GOOGLE_APPLICATION_CREDENTIALS"
        ):
            generate_jwt({})

    def test_passing_env_credentials(
        self,
        mocked_google_credentials,
        mocked_crypt,
        mocked_jwt,
        mocked_env_credentials_path,
    ):
        try:
            assert generate_jwt({}) == b"JWT_TOKEN"
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_using_kwargs_credentials(
        self, mocked_google_credentials, mocked_crypt, mocked_jwt
    ):
        try:
            generate_jwt(
                {}, google_application_credentials="/some/path/credentials.json"
            )
        except ValueError:
            pytest.fail("Unexpected ValueError")

    @freeze_time("2019-01-14 03:21:34")
    def test_setting_claims(self, mocked_google_credentials, mocked_crypt, mocked_jwt):
        claims = {}

        generate_jwt(
            claims, google_application_credentials="/some/path/credentials.json"
        )

        assert claims == {
            "aud": "https://api.fluidly.com",
            "email": "test@email.com",
            "exp": 1547439694,
            "iat": 1547436094,
            "iss": "test@email.com",
            "sub": "test@email.com",
        }

    def test_returning_jwt_with_google_credentials(
        self, mocked_google_credentials, mocked_crypt, mocked_jwt
    ):
        assert (
            generate_jwt(
                {}, google_application_credentials="/some/path/credentials.json"
            )
            == b"JWT_TOKEN"
        )

    def test_returning_jwt_from_auth0_env(
        self, mocked_auth0_jwt_token, mocked_crypt, mocked_jwt
    ):
        assert generate_jwt({}) == b"AUTH0_JWT_TOKEN"
