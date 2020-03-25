from typing import Any, TypeVar

from fluidly.auth.permissions import (
    UserPermissionsPayloadException as UserPermissionsPayloadException,
)
from fluidly.auth.permissions import (
    UserPermissionsRequestException as UserPermissionsRequestException,
)
from fluidly.auth.permissions import check_admin_permissions as check_admin_permissions
from fluidly.auth.permissions import check_user_permissions as check_user_permissions
from fluidly.flask.api_exception import APIException as APIException
from fluidly.flask.utils import base64_decode as base64_decode

T = TypeVar("T")

def authorised(f: T) -> T: ...
def admin(f: T) -> T: ...
