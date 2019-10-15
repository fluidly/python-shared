import json
from functools import wraps

from flask import g, request
from fluidly.auth.permissions import (
    UserPermissionsPayloadException,
    UserPermissionsRequestException,
    check_user_permissions,
)
from fluidly.flask.api_exception import APIException
from fluidly.flask.utils import base64_decode


def authorised(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Retrieves the authentication information from Google Cloud Endpoints
        and passes it to user permissions service"""
        encoded_user_info = request.headers.get("X-Endpoint-API-UserInfo", None)
        if not encoded_user_info:
            raise APIException(status=401, title="User is not authenticated")

        decoded_user_info = base64_decode(encoded_user_info)
        user_info = json.loads(decoded_user_info)
        claims = json.loads(user_info.get("claims", "{}"))

        auth0_claims = claims.get("https://api.fluidly.com/app_metadata", {})
        internal_claims = claims.get("https://api.fluidly.com/internal_metadata", {})

        connection_id = request.view_args["connection_id"]
        user_id = auth0_claims.get("userId", None)

        try:
            given_permissions = check_user_permissions(claims, connection_id)
            is_service_account = internal_claims.get("isServiceAccount", False)

            if not is_service_account and not given_permissions:
                raise APIException(status=403, title="User cannot access this resource")
        except (
            ValueError,
            UserPermissionsPayloadException,
            UserPermissionsRequestException,
        ):
            raise APIException(
                status=403, title="An issue occurred while fetching permissions"
            )

        g.connection_id = connection_id
        g.user_id = user_id
        return f(*args, **kwargs)

    return decorated_function