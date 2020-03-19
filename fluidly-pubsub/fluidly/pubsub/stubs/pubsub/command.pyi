from typing import Any, Callable, List, Tuple

from fluidly.pubsub.base_subscriber import (
    setup_base_subscriber as setup_base_subscriber,
)

Subscriptions = List[Tuple[str, Callable[[str], Any]]]
subscriber: Any

def setup_subscriptions(subscriptions: Subscriptions, **kwargs: Any) -> Any: ...
