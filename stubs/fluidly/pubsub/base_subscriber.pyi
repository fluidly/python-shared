from typing import Any

from fluidly.pubsub.exceptions import DropMessageException as DropMessageException
from fluidly.pubsub.message import Message as Message

GOOGLE_PROJECT: Any
APPLICATION_NAME: Any

def setup_base_subscriber(
    subscriber: Any, subscriptions: Any, **kwargs: Any
) -> None: ...
