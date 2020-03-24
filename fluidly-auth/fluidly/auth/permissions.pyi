from typing import Any, Optional

from fluidly.auth.jwt import generate_jwt as generate_jwt
from fluidly.auth.jwt_requests import make_jwt_request as make_jwt_request
from fluidly.structlog import base_logger as base_logger

class UserPermissionsRequestException(Exception): ...
class UserPermissionsPayloadException(Exception): ...

def get_fluidly_api_url(fluidly_api_url: Optional[Any] = ...): ...
def check_permissions(original_payload: Any, request_url: Any, **kwargs: Any): ...
def check_user_permissions(
    original_payload: Any, connection_id: Any, fluidly_api_url: Optional[Any] = ...
): ...
def check_admin_permissions(
    original_payload: Any, fluidly_api_url: Optional[Any] = ...
): ...
