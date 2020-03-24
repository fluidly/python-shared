from typing import Any, Callable, List, Tuple

Subscriptions = List[Tuple[str, Callable[[str], Any]]]
subscriber: Any

def setup_subscriptions(subscriptions: Subscriptions, **kwargs: Any) -> Any: ...
