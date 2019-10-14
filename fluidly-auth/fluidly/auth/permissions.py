import os
import time

from fluidly.auth.jwt import generate_jwt
from fluidly.auth.jwt_requests import make_jwt_request
from fluidly.structlog import base_logger


class UserPermissionsRequestException(Exception):
    pass


class UserPermissionsPayloadException(Exception):
    pass


def check_user_permissions(original_payload, connection_id, user_permissions_url=None):
    if not user_permissions_url:
        user_permissions_url = os.getenv("USER_PERMISSIONS_URL")

    if not user_permissions_url:
        raise ValueError("Please provide USER_PERMISSIONS_URL")

    start = time.time()
    signed_jwt = generate_jwt(original_payload)
    request_url = f"{user_permissions_url}/connections/{connection_id}"

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
