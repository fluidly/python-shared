import json
import os
import time
from typing import Any, Mapping, Optional, Tuple

from google.auth import crypt, jwt
from google.auth.crypt.base import Signer
from google.oauth2.service_account import Credentials

audience = "https://api.fluidly.com"


def get_service_account_and_signer(
    path: Optional[str], info: Optional[Mapping[str, str]]
) -> Tuple[str, Signer]:
    try:
        if path is not None:
            return Credentials.from_service_account_file(
                path
            ).service_account_email, crypt.RSASigner.from_service_account_file(path)
        elif info is not None:
            return Credentials.from_service_account_info(
                info
            ).service_account_email, crypt.RSASigner.from_service_account_info(info)
        else:
            raise ValueError("Credentials path or info must be set")
    except FileNotFoundError or AttributeError:
        raise Exception("Credentials must be a path or json")


def generate_jwt(
    claims: Any,
    google_application_credentials: Optional[str] = None,
    google_application_credentials_info: Optional[str] = None,
) -> bytes:
    """Generates a signed JSON Web Token using a Google API Service Account."""

    auth0_jwt_token = os.getenv("AUTH0_JWT_TOKEN")
    if auth0_jwt_token:
        return auth0_jwt_token.encode()

    if google_application_credentials is None:
        google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    parsed_google_application_credentials_info = None
    if google_application_credentials_info is None:
        google_application_credentials_info = os.getenv("GOOGLE_CREDENTIALS")
    if google_application_credentials_info:
        parsed_google_application_credentials_info = json.loads(
            google_application_credentials_info
        )

    if not google_application_credentials and not google_application_credentials_info:
        raise ValueError(
            "Please provide GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS"
        )

    now = int(time.time())

    sa_email, signer = get_service_account_and_signer(
        google_application_credentials, parsed_google_application_credentials_info
    )

    payload = {
        "iat": now,
        "exp": now + 3600,
        # iss must match 'issuer' in the security configuration in your
        # swagger spec (e.g. service account email). It can be any string.
        "iss": sa_email,
        # aud must be either your Endpoints service name, or match the value
        # specified as the 'x-google-audience' in the OpenAPI document.
        "aud": audience,
        # sub and email should match the service account's email address
        "sub": sa_email,
        "email": sa_email,
    }

    claims.update(payload)

    jwt_string: bytes = jwt.encode(signer, claims)

    return jwt_string
