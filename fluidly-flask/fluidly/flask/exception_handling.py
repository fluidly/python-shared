from functools import wraps

from fluidly.flask.api_exception import APIException
from fluidly.structlog.base_logger import rest_log_entrypoint
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest


def handle_exceptions(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except APIException as exception:
            raise exception
        except ValidationError as exception:
            raise APIException(
                title="Schema Validation Error",
                status=422,
                detail=exception.normalized_messages(),
            )
        except BadRequest as exception:
            raise APIException(
                title="Invalid Body", status=400, detail=exception.description
            )
        except Exception:
            raise APIException(status=500, title="An unknown error occurred")
        return result

    return decorated_function


def log_safely(func):
    @wraps(func)
    @rest_log_entrypoint
    @handle_exceptions
    def decorated_function(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated_function