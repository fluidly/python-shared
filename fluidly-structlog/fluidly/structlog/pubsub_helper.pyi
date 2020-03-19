from fluidly.structlog.base_logger import get_logger as get_logger
from typing import TypeVar

T = TypeVar('T')

def pubsub_log_entrypoint(func: T)-> T: ...
def pubsub_log_entrypoint_class(func: T)-> T: ...
