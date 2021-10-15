import os
from typing import Any, Callable, List, Tuple

from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture

from fluidly.pubsub.exceptions import DropMessageException
from fluidly.pubsub.message import Message

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")
APPLICATION_NAME = os.getenv("APPLICATION_NAME")


Deserialiser = Callable[[Message], Any]
MessageHandler = Callable[[Message], Any]
Subscriptions = List[Tuple[str, MessageHandler]]
SubscriptionFutures = List[StreamingPullFuture]


def setup_base_subscriber(
    subscriber: SubscriberClient, subscriptions: Subscriptions, **kwargs: Any
) -> SubscriptionFutures:
    return [
        subscriber.subscribe(
            subscriber.subscription_path(GOOGLE_PROJECT, subscription_name),
            callback=generate_callback(Message, message_handler),
            **kwargs
        )
        for subscription_name, message_handler in subscriptions
    ]


def generate_callback(
    deserialiser: Deserialiser, message_handler: MessageHandler
) -> Callable[[Message], Any]:
    def callback(message: Message) -> None:
        deserialised_message = deserialiser(message)

        try:
            attributes = dict(message.attributes) if message.attributes else None
            if (
                attributes
                and "audience" in attributes
                and attributes["audience"]
                and APPLICATION_NAME not in attributes["audience"]
            ):
                message.ack()
                return

            message_handler(deserialised_message)

        except DropMessageException:
            message.ack()

    return callback
