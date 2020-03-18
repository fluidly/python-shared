from fluidly.pubsub.exceptions import DropMessageException


def test_drop_message_exception_default():
    try:
        raise DropMessageException()
    except DropMessageException as e:
        assert not e.reraise


def test_drop_message_exception_reraise():
    try:
        raise DropMessageException(reraise=True)
    except DropMessageException as e:
        assert e.reraise
