from unittest import mock

from fluidly.pubsub.fake_publisher import FakePublisher


def test_fake_publisher_passes_on_messages():
    m = mock.Mock()

    def mock_consumer(session, message):
        assert message.data == {}
        assert session == fake_session
        m.called = True

    fake_session = "fake session"
    topic = "notes topic"
    subscriptions = [(topic, mock_consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}")
    assert m.called


def test_fake_publisher_passes_on_messages_in_different_call_args():
    m = mock.Mock()

    def mock_consumer(message, session):
        assert message.data == {}
        assert session == fake_session
        m.called = True

    fake_session = "fake session"
    topic = "notes topic"
    subscriptions = [(topic, mock_consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(topic, "{}")
    assert m.called


def test_fake_publisher_handles_no_session():
    m = mock.Mock()

    def mock_consumer(message, session):
        assert message.data == {}
        m.called = True
        assert session is None

    topic = "notes topic"
    subscriptions = [(topic, mock_consumer)]

    fake_publisher = FakePublisher(subscriptions=subscriptions)

    fake_publisher.publish(topic, "{}")
    assert m.called

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


def test_fake_publisher_has_last_call_attribute():
    fake_session = "fake session"
    topic = "notes topic"

    consumer = mock.Mock()
    subscriptions = [(topic, consumer)]

    fake_publisher = FakePublisher(fake_session, subscriptions)

    fake_publisher.publish(
        topic, '{"first": "message"}', connection_id="first_connection_id"
    )
    fake_publisher.publish(
        topic,
        '{"last": "message"}',
        some_attribute="stuff",
        connection_id="last_connection_id",
    )

    last_published_message_data = fake_publisher.topics_called[
        topic
    ].last_published_message_data
    last_published_message_attributes = fake_publisher.topics_called[
        topic
    ].last_published_message_attributes

    assert last_published_message_data == '{"last": "message"}'
    assert last_published_message_attributes["connection_id"] == "last_connection_id"
    assert last_published_message_attributes["some_attribute"] == "stuff"
