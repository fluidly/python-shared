from typing import Any, Callable

from fluidly.pubsub.message import Message as Message

GOOGLE_PROJECT: Any
APPLICATION_NAME: Any

def setup_base_subscriber(
    subscriber: Any, subscriptions: Any, **kwargs: Any
) -> None: ...
def generate_callback(
    deserialiser: Any, message_handler: Callable[[Message], Any]
) -> Any: ...
