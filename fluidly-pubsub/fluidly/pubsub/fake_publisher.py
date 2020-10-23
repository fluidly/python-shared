import json
from collections import defaultdict

from fluidly.pubsub.tests import message_from_dict


class MessageFuture:
    def result(self):
        pass


class TopicSpy:
    def __init__(self):
        self.call_count = 0
        self.call_list = []


class FakePublisher:
    def __init__(self, session, subscriptions=[]):
        self.session = session
        self.subscriptions = dict(subscriptions)
        self.topics_called = defaultdict(TopicSpy)

    def publish(self, topic, data, connection_id=""):

        if topic in self.subscriptions:
            self.subscriptions[topic](self.session, message_from_dict(json.loads(data)))
        self.topics_called[topic].call_count += 1
        self.topics_called[topic].call_list.append(data)
        return MessageFuture()

    def topic_path(self, project, topic):
        return topic
