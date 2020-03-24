from typing import Any

from fluidly.flask.api_exception import APIException as APIException
from fluidly.flask.rest_logger import rest_log_entrypoint as rest_log_entrypoint

def handle_exceptions(func: Any): ...
def log_safely(func: Any): ...
