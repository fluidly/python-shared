import json
import os
from collections import namedtuple
from tempfile import NamedTemporaryFile, TemporaryDirectory

from fluidly.pubsub.tests import (
    message_from_dict,
    message_from_fixture,
    message_from_tuple,
    mock_message,
)


def test_mock_message():
    mocked_message = mock_message('{"some": "payload"}', {"some": "attributes"})

    assert mocked_message.data == {"some": "payload"}
    assert mocked_message.attributes == {"some": "attributes"}


def test_message_from_dict():
    mocked_message_from_dict = message_from_dict(
        {"some": "payload"}, {"some": "attributes"}
    )

    assert mocked_message_from_dict.data == {"some": "payload"}
    assert mocked_message_from_dict.attributes == {"some": "attributes"}


def test_message_from_tuple():
    SomeTuple = namedtuple("SomeTuple", ["a", "b"])
    some_tuple = SomeTuple(a=1, b=2)

    mocked_message_from_tuple = message_from_tuple(some_tuple, {"some": "attributes"})

    assert mocked_message_from_tuple.data == {"a": 1, "b": 2}
    assert mocked_message_from_tuple.attributes == {"some": "attributes"}


def test_message_from_fixture():
    payload = {"some": "payload"}
    attributes = {"some": "attributes"}

    with TemporaryDirectory() as tempdir:
        with NamedTemporaryFile(dir=tempdir) as f:
            f.write(json.dumps(payload).encode("utf-8"))
            f.seek(0)

            path = os.path.join(tempdir, f.name)

            mocked_message = message_from_fixture(path, attributes)
            assert mocked_message.data == payload
            assert mocked_message.attributes == attributes
