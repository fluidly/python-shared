import json

from fluidly.pubsub.exceptions import DropMessageException


class Message:
    def __init__(self, message):
        self.message = message
        self.attributes = dict(message.attributes) if message.attributes else {}
        self.data = json.loads(message.data)
        self.publish_time = message.publish_time

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError as e:
            raise DropMessageException() from e
