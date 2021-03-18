import json
from typing import Any

from google.cloud.pubsub_v1.types import PubsubMessage

from fluidly.pubsub.exceptions import DropMessageException


class Message:
    def __init__(self, message: PubsubMessage) -> None:
        self.message = message
        self.attributes = dict(message.attributes) if message.attributes else {}
        self.data = json.loads(message.data)
        self.publish_time = message.publish_time

    def __getattr__(self, attr: str) -> Any:
        try:
            return self.data[attr]
        except KeyError as e:
            raise DropMessageException() from e
