from typing import TypeVar

from fluidly.structlog.base_logger import get_logger as get_logger

T = TypeVar("T")

def pubsub_log_entrypoint(func: T) -> T: ...
def pubsub_log_entrypoint_class(func: T) -> T: ...
