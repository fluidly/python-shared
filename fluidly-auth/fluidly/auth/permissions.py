import os
import time

from fluidly.auth.jwt import generate_jwt
from fluidly.auth.jwt_requests import make_jwt_request
from fluidly.structlog import base_logger


class UserPermissionsRequestException(Exception):
    pass


class UserPermissionsPayloadException(Exception):
    pass


def check_user_permissions(original_payload, connection_id, fluidly_api_url=None):
    if not fluidly_api_url:
        fluidly_api_url = os.getenv("FLUIDLY_API_URL")

    if not fluidly_api_url:
        raise ValueError("Please provide FLUIDLY_API_URL")

    start = time.time()
    signed_jwt = generate_jwt(original_payload)
    request_url = f"{fluidly_api_url}/v1/user-permissions/connections/{connection_id}"

    try:
        response = make_jwt_request(signed_jwt, request_url)
    except Exception:
        raise UserPermissionsRequestException()

    logger = base_logger.get_logger()
    end = time.time()

    try:
        response_json = response.json()

        authorised = response.status_code == 200 and response_json.get("grantAccess")
        if not authorised:
            logger.warning(
                "Authorisation failed",
                response_json=response_json,
                status_code=response.status_code,
                connection_id=connection_id,
                response_headers=response.headers,
                url=request_url,
                original_payload=original_payload,
                duration=end - start,
            )
            return False
        logger.info(
            "Called user permissions",
            response_json=response_json,
            status_code=response.status_code,
            connection_id=connection_id,
            url=request_url,
            duration=end - start,
        )
        return True
    except Exception:
        logger.warning(
            "Authorisation failed",
            status_code=response.status_code,
            connection_id=connection_id,
            response_headers=response.headers,
            url=request_url,
            original_payload=original_payload,
            exc_info=True,
            duration=end - start,
        )
        raise UserPermissionsPayloadException()
