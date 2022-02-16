import time
from functools import wraps
from typing import Any

from sqlalchemy.orm.session import Session
from typing_extensions import Protocol

from fluidly.pubsub.message import Message
from fluidly.structlog.base_logger import get_logger


class MessageCallback(Protocol):
    __qualname__: str

    def __call__(self, message: Message, *args: Any, **kwargs: Any) -> None:
        ...


class SessionMessageCallback(Protocol):
    __qualname__: str

    def __call__(
        self, session: Session, message: Message, *args: Any, **kwargs: Any
    ) -> None:
        ...


def pubsub_log_entrypoint(func: MessageCallback):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        logger = get_logger()
        logger = logger.new(callback=func.__qualname__)
        start = time.time()

        publish_time = message.publish_time
        message_age = time.time() - publish_time.timestamp()

        try:
            result = func(message, *args, **kwargs)
        except Exception:
            end = time.time()
            logger.error(
                "pubsub_message_processed",
                duration=end - start,
                success=False,
                exc_info=True,
                message=message.data,
                message_age=message_age,
                attributes=message.attributes,
                connection_id=message.attributes.get("connection_id"),
            )
            raise

        end = time.time()
        logger.info(
            "pubsub_message_processed",
            duration=end - start,
            success=True,
            connection_id=message.attributes.get("connection_id"),
        )
        return result

    return wrapper


def pubsub_log_entrypoint_class(func: SessionMessageCallback):
    @wraps(func)
    def wrapper(self, session, message, *args, **kwargs):
        logger = get_logger()
        logger = logger.new(callback=func.__qualname__)
        start = time.time()

        publish_time = message.publish_time
        message_age = time.time() - publish_time.timestamp()
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
                message_age=message_age,
                attributes=message.attributes,
                connection_id=message.attributes.get("connection_id"),
            )
            raise

        end = time.time()
        logger.info(
            "pubsub_message_processed",
            duration=end - start,
            success=True,
            connection_id=message.attributes.get("connection_id"),
        )
        return result

    return wrapper
