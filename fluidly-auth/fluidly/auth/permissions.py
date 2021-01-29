import os
import time
from typing import Any, Optional

from fluidly.auth.jwt import generate_jwt
from fluidly.auth.jwt_requests import make_jwt_request
from fluidly.structlog import base_logger


class UserPermissionsRequestException(Exception):
    pass


class UserPermissionsPayloadException(Exception):
    pass


def get_fluidly_api_url(fluidly_api_url: Optional[str] = None) -> str:
    if not fluidly_api_url:
        fluidly_api_url = os.getenv("FLUIDLY_API_URL")

    if not fluidly_api_url:
        raise ValueError("Please provide FLUIDLY_API_URL")
    return fluidly_api_url


def check_permissions(original_payload: Any, request_url: str, **kwargs: Any) -> bool:
    start = time.time()
    signed_jwt = generate_jwt(original_payload)
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
                response_headers=response.headers,
                url=request_url,
                original_payload=original_payload,
                duration=end - start,
                **kwargs,
            )
            return False
        logger.info(
            "Called user permissions",
            response_json=response_json,
            status_code=response.status_code,
            url=request_url,
            duration=end - start,
        )
        return True
    except Exception:
        logger.warning(
            "Authorisation failed",
            status_code=response.status_code,
            response_headers=response.headers,
            url=request_url,
            original_payload=original_payload,
            exc_info=True,
            duration=end - start,
        )
        raise UserPermissionsPayloadException()


def check_user_permissions(
    original_payload: Any, connection_id: str, fluidly_api_url: Optional[str] = None
) -> bool:
    return check_permissions(
        original_payload,
        f"{get_fluidly_api_url(fluidly_api_url)}/v1/user-permissions/connections/{connection_id}",
        connection_id=connection_id,
    )


def check_admin_permissions(
    original_payload: Any, fluidly_api_url: Optional[str] = None
) -> bool:
    return check_permissions(
        original_payload,
        f"{get_fluidly_api_url(fluidly_api_url)}/v1/user-permissions/admin",
    )
