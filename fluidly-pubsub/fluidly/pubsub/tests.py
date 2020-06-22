import datetime
import json
from collections import namedtuple
from unittest import mock

from fluidly.pubsub.message import Message


def mock_message(payload: str, attributes: dict = None):
    pubsub_message = mock.Mock()
    pubsub_message.data = payload
    pubsub_message.attributes = attributes
    pubsub_message.publish_time = datetime.datetime.now()

    return Message(pubsub_message)


def message_from_dict(payload_dict: dict, attributes: dict = None):
    dict_as_json = json.dumps(payload_dict)
    return mock_message(dict_as_json, attributes)


def message_from_tuple(payload_tuple: namedtuple, attributes: dict = None):
    tuple_as_json = json.dumps(payload_tuple._asdict())
    return mock_message(tuple_as_json, attributes)


def message_from_fixture(path: str, attributes: dict = None):
    with open(path, "r") as fixture:
        return mock_message(fixture.read(), attributes)
