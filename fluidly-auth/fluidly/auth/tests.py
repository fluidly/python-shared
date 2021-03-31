import json
from base64 import b64encode


def request_headers(
    if_modified_since=None, service_account=False, email=None, name=None
):
    # Claims attribute is in string format in the header provided by Cloud Endpoints
    claims = {
        "https://api.fluidly.com/internal_metadata": {
            "isServiceAccount": service_account
        },
        "https://api.fluidly.com/user_metadata": {},
        "https://api.fluidly.com/app_metadata": {"userId": "1"},
        "iss": "https://fluidly.eu.auth0.com/",
        "sub": "auth0|5cb644d401c03f119f1ed772",
        "aud": ["https://api.fluidly.com", "https://fluidly.eu.auth0.com/userinfo"],
        "iat": 1555519624,
        "exp": 1555526824,
        "azp": "5HIxj76CRK3QCxUa2KlUwJw7vBCly9e5",
        "scope": "openid email",
    }

    if email is not None:
        claims["https://api.fluidly.com/email"] = email

    if name is not None:
        claims["https://api.fluidly.com/name"] = name

    endpoint_header = json.dumps(
        {
            "claims": json.dumps(claims),
            "issuer": "https://fluidly.eu.auth0.com/",
            "id": "auth0|5cb644d401c03f119f1ed772",
        }
    )
    headers = {
        "X-Endpoint-Api-Userinfo": b64encode(endpoint_header.encode("utf-8")),
        "Content-Type": "application/json",
    }
    if if_modified_since is not None:
        headers["If-Modified-Since"] = if_modified_since

    return headers
