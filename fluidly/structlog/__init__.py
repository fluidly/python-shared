import time
from contextlib import contextmanager
from functools import wraps

import structlog
from structlog import get_logger
from structlog.threadlocal import wrap_dict

structlog.configure(
    processors=[
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=wrap_dict(dict),
)


@contextmanager
def log_duration(key_name):
    """Logs duration of block and binds result to structlog

    Arguments:
        key_name {str} -- Key to bind the result
    """
    log = get_logger()
    start_time = time.time()

    yield

    end_time = time.time()
    log.bind(**{key_name: end_time - start_time})


def pubsub_log_entrypoint(func):
    @wraps(func)
    def wrapper(self, session, message, *args, **kwargs):
        logger = get_logger()
        logger = logger.new(callback=func.__qualname__)
        start = time.time()

        try:
            result = func(self, session, message, *args, **kwargs)
        except Exception:
            end = time.time()
            logger.error(
                "pubsub_message_processed",
                duration=end - start,
                success=False,
                exc_info=True,
                message=message.data,
                attributes=message.attributes,
                connection_id=message.attributes.get("connection_id"),
            )
            raise

        end = time.time()
        logger.info(
            "pubsub_message_processed",
            duration=end - start,
            success=True,
            attributes=message.attributes,
            connection_id=message.attributes.get("connection_id"),
        )
        return result

    return wrapper
