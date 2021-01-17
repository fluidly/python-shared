import json
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

from fluidly.pubsub.message import Message
from fluidly.pubsub.tests import message_from_dict


class MessageFuture:
    def result(self) -> None:
        pass


class TopicSpy:
    def __init__(self) -> None:
        self.call_count = 0
        self.call_list: List[str] = []


class FakePublisherDeprecated:
    def __init__(
        self, session: Any, subscriptions: List[Tuple[str, Callable[..., Message]]] = []
    ) -> None:
        self.session = session
        self.subscriptions = dict(subscriptions)
        self.topics_called: Dict[str, TopicSpy] = defaultdict(TopicSpy)

    def publish(self, topic: str, data: str, connection_id: str = "") -> MessageFuture:

        if topic in self.subscriptions:
            self.subscriptions[topic](self.session, message_from_dict(json.loads(data)))
        self.topics_called[topic].call_count += 1
        self.topics_called[topic].call_list.append(data)
        return MessageFuture()

    def topic_path(self, project: str, topic: str) -> str:
        return topic


class FakePublisher:
    def __init__(
        self, session: Any, subscriptions: List[Tuple[str, Callable[..., Message]]] = []
    ) -> None:
        self.session = session
        self.subscriptions = dict(subscriptions)
        self.topics_called: Dict[str, TopicSpy] = defaultdict(TopicSpy)

    def publish(self, topic: str, data: str, **attrs: Any) -> MessageFuture:
        if topic in self.subscriptions:
            self.subscriptions[topic](
                message_from_dict(json.loads(data)), self.session, attrs
            )
        self.topics_called[topic].call_count += 1
        self.topics_called[topic].call_list.append(data)
        return MessageFuture()

    def topic_path(self, project: str, topic: str) -> str:
        return topic
