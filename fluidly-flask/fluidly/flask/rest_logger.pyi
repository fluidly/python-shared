from typing import Any

from fluidly.flask.api_exception import APIException as APIException
from fluidly.structlog import base_logger as base_logger

def rest_log_entrypoint(func: Any): ...
