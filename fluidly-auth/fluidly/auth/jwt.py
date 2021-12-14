import os
import time
from typing import Any, Optional, Union

from google.auth import crypt, jwt
from google.oauth2.service_account import Credentials

audience: str = "https://api.fluidly.com"


def get_service_account_and_signer(
    path: Union[str, None], info: Union[str, None]
) -> Any:
    try:
        if path is not None:
            return Credentials.from_service_account_file(
                path
            ).service_account_email, crypt.RSASigner.from_service_account_file(path)
        elif info is not None:
            return Credentials.from_service_account_info(
                info
            ).service_account_email, crypt.RSASigner.from_service_account_info(info)
    except FileNotFoundError or AttributeError:
        raise Exception("Credentials must be a path or json")


def generate_jwt(
    claims: Any,
    google_application_credentials: Optional[Any] = None,
    google_application_credentials_info: Optional[Any] = None,
) -> Any:
    """Generates a signed JSON Web Token using a Google API Service Account."""

    if os.getenv("AUTH0_JWT_TOKEN"):
        return os.getenv("AUTH0_JWT_TOKEN")

    if not google_application_credentials:
        google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not google_application_credentials_info:
        google_application_credentials_info = os.getenv("GOOGLE_CREDENTIALS")

    if not google_application_credentials and not google_application_credentials_info:
        raise ValueError(
            "Please provide GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS"
        )

    now = int(time.time())

    sa_email, signer = get_service_account_and_signer(
        google_application_credentials, google_application_credentials_info
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

    jwt_string = jwt.encode(signer, claims)

    return jwt_string
