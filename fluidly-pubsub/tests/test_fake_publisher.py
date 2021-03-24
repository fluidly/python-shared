from unittest import mock

from fluidly.pubsub.fake_publisher import FakePublisher


def test_fake_publisher_passes_on_messages():
    fake_session = "fake session"
    topic = "notes topic"
    consumer = mock.Mock()
    subscriptions = [(topic, consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}")

    args, kwargs = consumer.call_args
    session, message = args
    assert session == fake_session
    assert message.data == {}


def test_fake_publisher_records_calls():
    fake_session = "fake session"
    topic = "notes topic"
    another_topic = "not a real topic"
    consumer = mock.Mock()
    subscriptions = [(topic, consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}")

    calls = fake_publisher.topics_called

    assert calls[topic].call_count == 1
    assert calls[topic].call_list == ["{}"]

    assert calls[another_topic].call_count == 0
    assert calls[another_topic].call_list == []


def test_fake_publisher_records_calls_with_additional_attributes():
    fake_session = "fake session"
    topic = "notes topic"

    consumer = mock.Mock()
    subscriptions = [(topic, consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}", additional_attribute="1234")

    topics_called = fake_publisher.topics_called

    assert topics_called[topic].call_count == 1
    assert topics_called[topic].call_list == ["{}"]
    assert topics_called[topic].calls[0][1]["additional_attribute"] == "1234"
    assert topics_called[topic].calls[0][1]["connection_id"] == ""


def test_fake_publisher_records_calls_with_connection_id():
    fake_session = "fake session"
    topic = "notes topic"

    consumer = mock.Mock()
    subscriptions = [(topic, consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}", connection_id="some_connection_id")

    topics_called = fake_publisher.topics_called

    assert topics_called[topic].calls[0][1]["connection_id"] == "some_connection_id"
