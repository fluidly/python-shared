from fluidly.pubsub.exceptions import DropMessageException as DropMessageException
from fluidly.pubsub.message import Message as Message
from typing import Any

GOOGLE_PROJECT: Any
APPLICATION_NAME: Any

def setup_base_subscriber(subscriber: Any, subscriptions: Any, **kwargs: Any) -> None: ...
def generate_callback(deserialiser: Any, message_handler: Any): ...
