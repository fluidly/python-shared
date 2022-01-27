from typing import Any, Optional

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1 import SubscriberClient

from fluidly.pubsub.base_subscriber import (
    SubscriptionFutures,
    Subscriptions,
    setup_base_subscriber,
)

_subscriber: Optional[SubscriberClient] = None


def get_pubsub_subscriber() -> SubscriberClient:
    global _subscriber

    if _subscriber is None:
        _subscriber = pubsub_v1.SubscriberClient()
    return _subscriber


def setup_subscriptions(
    subscriptions: Subscriptions, **kwargs: Any
) -> SubscriptionFutures:
    subscriber = get_pubsub_subscriber()
    return setup_base_subscriber(subscriber, subscriptions, **kwargs)
