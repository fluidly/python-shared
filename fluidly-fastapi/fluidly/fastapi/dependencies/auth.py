import json
from typing import Any, Dict

from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from fluidly.auth.permissions import (
    UserPermissionsPayloadException,
    UserPermissionsRequestException,
    check_admin_permissions,
    check_user_permissions,
)
from fluidly.fastapi.utils import base64_decode


def get_authorised_user(request: Request) -> Dict[str, Any]:
    """Retrieves the authentication information from Google Cloud Endpoints
    and passes it to user permissions service"""
    encoded_user_info = request.headers.get("X-Endpoint-API-UserInfo", None)
    if not encoded_user_info:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    decoded_user_info = base64_decode(encoded_user_info)
    user_info = json.loads(decoded_user_info)
    claims = json.loads(user_info.get("claims", "{}"))

    email = claims.get("https://api.fluidly.com/email", None)
    name = claims.get("https://api.fluidly.com/name", None)
    auth0_claims = claims.get("https://api.fluidly.com/app_metadata", {})
    internal_claims = claims.get("https://api.fluidly.com/internal_metadata", {})

    connection_id = request.path_params["connection_id"]
    user_id = auth0_claims.get("userId", None)

    try:
        is_service_account = internal_claims.get("isServiceAccount", False)

        if not is_service_account and not check_user_permissions(claims, connection_id):
            raise HTTPException(
                status_code=403, detail="User cannot access this resource"
            )
    except (
        ValueError,
        UserPermissionsPayloadException,
        UserPermissionsRequestException,
    ):
        raise HTTPException(
            status_code=403, detail="An issue occurred while fetching permissions"
        )

    return {
        "connection_id": connection_id,
        "user_id": user_id,
        "email": email,
        "name": name,
    }


def get_admin_user(request: Request) -> Dict[str, Any]:
    """Retrieves the authentication information from Google Cloud Endpoints and passes it to user permissions service"""
    encoded_info = request.headers.get("X-Endpoint-API-UserInfo", None)
    if not encoded_info:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    info_json = base64_decode(encoded_info)
    # First parsing of the decoded header string
    user_info = json.loads(info_json)
    # Claims are given as a string by Cloud Endpoints so we have
    # to parse the claims attribute
    claims = json.loads(user_info.get("claims", "{}"))

    email = claims.get("https://api.fluidly.com/email", None)
    name = claims.get("https://api.fluidly.com/name", None)
    auth0_claims = claims.get("https://api.fluidly.com/app_metadata", {})
    internal_claims = claims.get("https://api.fluidly.com/internal_metadata", {})

    user_id_from_token = auth0_claims.get("userId", None)

    try:
        is_service_account = internal_claims.get("isServiceAccount", False)

        if not is_service_account and not check_admin_permissions(claims):
            raise HTTPException(
                status_code=403, detail="User cannot access this resource"
            )
    except (
        ValueError,
        UserPermissionsPayloadException,
        UserPermissionsRequestException,
    ):
        raise HTTPException(
            status_code=403, detail="An issue occurred while fetching permissions"
        )

    return {"user_id": user_id_from_token, "email": email, "name": name}
