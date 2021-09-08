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
        self.calls: List[List[Any]] = []

    @property
    def last_published_message_json(self) -> Any:
        return json.loads(self.last_published_message_data)

    @property
    def last_published_message_data(self) -> Any:
        return self.calls[-1][0]

    @property
    def last_published_message_attributes(self) -> Any:
        return self.calls[-1][1]


class FakePublisher:
    def __init__(
        self,
        session: Any = None,
        subscriptions: List[Tuple[str, Callable[..., Message]]] = [],
    ) -> None:
        self.session = session
        self.subscriptions = dict(subscriptions)
        self.topics_called: Dict[str, TopicSpy] = defaultdict(TopicSpy)

    def publish(
        self, topic: str, data: str, connection_id: str = "", **attrs: Any
    ) -> MessageFuture:

        for attr in attrs.values():
            if not isinstance(attr, str):
                raise ValueError("Non-string attribute detected")

        if topic in self.subscriptions:
            self.subscriptions[topic](
                session=self.session, message=message_from_dict(json.loads(data))
            )
        self.topics_called[topic].call_count += 1
        self.topics_called[topic].call_list.append(data)
        self.topics_called[topic].calls.append(
            [data, {**attrs, "connection_id": connection_id}]
        )

        return MessageFuture()

    def topic_path(self, project: str, topic: str) -> str:
        return topic
