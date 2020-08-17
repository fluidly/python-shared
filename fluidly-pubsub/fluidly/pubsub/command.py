from typing import Any, Callable, List, Tuple

from google.cloud import pubsub_v1

from fluidly.pubsub.base_subscriber import setup_base_subscriber
from fluidly.pubsub.message import Message

Subscriptions = List[Tuple[str, Callable[[Message], Any]]]

subscriber = pubsub_v1.SubscriberClient()


def setup_subscriptions(subscriptions: Subscriptions, **kwargs: Any) -> None:
    setup_base_subscriber(subscriber, subscriptions, **kwargs)
