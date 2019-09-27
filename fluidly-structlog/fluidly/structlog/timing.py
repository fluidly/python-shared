import time
from contextlib import contextmanager

from fluidly.structlog.base_logger import get_logger


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
