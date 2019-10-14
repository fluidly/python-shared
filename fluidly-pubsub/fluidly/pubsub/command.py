from typing import Any, Callable, List, Tuple

from fluidly.pubsub.base_subscriber import setup_base_subscriber
from google.cloud import pubsub_v1

Subscriptions = List[Tuple[str, Callable[[str], Any]]]

subscriber = pubsub_v1.SubscriberClient()


def setup_subscriptions(subscriptions: Subscriptions, **kwargs):
    setup_base_subscriber(subscriber, subscriptions, **kwargs)
