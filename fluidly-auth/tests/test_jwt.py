import json
from unittest import mock

import pytest
from freezegun import freeze_time
from google.oauth2.service_account import Credentials

from fluidly.auth import jwt
from fluidly.auth.jwt import generate_jwt


class MockCredentials:
    service_account_email = "test@email.com"


@pytest.fixture()
def mock_google_credentials(monkeypatch):
    def mock_credentials_from_file(path):
        assert type(path) == str
        return MockCredentials()

    def mock_credentials_from_info(info):
        assert type(info) == dict
        return MockCredentials()

    monkeypatch.setattr(
        Credentials, "from_service_account_file", mock_credentials_from_file
    )
    monkeypatch.setattr(
        Credentials, "from_service_account_info", mock_credentials_from_info
    )


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
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/some/path/credentials.json")


@pytest.fixture()
def mocked_env_credentials(monkeypatch):
    monkeypatch.setenv("GOOGLE_CREDENTIALS", '{ "private_key":"very private"}')


@pytest.fixture()
def mocked_auth0_jwt_token(monkeypatch):
    monkeypatch.setenv("AUTH0_JWT_TOKEN", "AUTH0_JWT_TOKEN")


class TestGenerateJWT:
    def test_required_credentials(self):
        with pytest.raises(
            ValueError,
            match="Please provide GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS",
        ):
            generate_jwt({})

    def test_passing_env_path_credentials(
        self,
        mocked_crypt,
        mocked_jwt,
        mocked_env_credentials_path,
        mock_google_credentials,
    ):
        try:
            assert generate_jwt({}) == b"JWT_TOKEN"
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_passing_env_credentials(
        self, mocked_crypt, mocked_jwt, mocked_env_credentials, mock_google_credentials
    ):
        try:
            assert generate_jwt({}) == b"JWT_TOKEN"
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test_using_kwargs_credentials(
        self, mocked_crypt, mocked_jwt, mock_google_credentials
    ):
        try:
            generate_jwt(
                {}, google_application_credentials="/some/path/credentials.json"
            )
        except ValueError:
            pytest.fail("Unexpected ValueError")

    @freeze_time("2019-01-14 03:21:34")
    def test_setting_claims(self, mocked_crypt, mocked_jwt, mock_google_credentials):
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

    def test_returning_jwt_with_google_credentials_path(
        self, mocked_crypt, mocked_jwt, mock_google_credentials
    ):
        assert (
            generate_jwt(
                {}, google_application_credentials="/some/path/credentials.json"
            )
            == b"JWT_TOKEN"
        )

    def test_returning_jwt_with_google_credentials(
        self, mocked_crypt, mocked_jwt, mock_google_credentials
    ):
        jwt = generate_jwt(
            {}, google_application_credentials_info='{"private_key":"very private"}'
        )
        assert jwt == b"JWT_TOKEN"

    def test_returning_jwt_from_auth0_env(
        self, mocked_auth0_jwt_token, mocked_crypt, mocked_jwt
    ):
        assert generate_jwt({}) == b"AUTH0_JWT_TOKEN"

    def test_raises_error_if_not_path(self):
        with pytest.raises(Exception, match="Credentials must be a path or json"):
            generate_jwt({}, google_application_credentials="not a file path")

    def test_raises_error_if_not_json_string(self):
        with pytest.raises(json.decoder.JSONDecodeError):
            generate_jwt({}, google_application_credentials_info="not an object")
