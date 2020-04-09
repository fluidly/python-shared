import time
from functools import wraps

from flask import request

from fluidly.flask.api_exception import APIException
from fluidly.structlog import base_logger


def rest_log_entrypoint(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        headers = dict(request.headers)

        connection_id_from_path = request.view_args.get("connection_id")
        partner_id_from_path = request.view_args.get("partner_id")

        logger = base_logger.get_logger()
        logger = logger.new(callback=func.__qualname__)
        start = time.time()

        try:
            result = func(*args, **kwargs)
        except APIException as exception:
            end = time.time()
            logger.error(
                "rest_request_processed",
                duration=end - start,
                success=False,
                exc_info=True,
                connection_id=connection_id_from_path,
                partner_id=partner_id_from_path,
                headers=headers,
                args=dict(request.view_args),
                status_code=exception.status,
                url=request.full_path,
            )
            raise exception

        end = time.time()
        logger.info(
            "rest_request_processed",
            duration=end - start,
            success=True,
            connection_id=connection_id_from_path,
            partner_id=partner_id_from_path,
            headers=headers,
            args=dict(request.view_args),
            status_code=result.status_code,
            url=request.full_path,
        )
        return result

    return decorated_function
