import os

from fluidly.pubsub.exceptions import DropMessageException
from fluidly.pubsub.message import Message

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")
APPLICATION_NAME = os.getenv("APPLICATION_NAME")


def setup_base_subscriber(subscriber, subscriptions):
    for subscription_name, message_handler in subscriptions:
        subscriber.subscribe(
            subscriber.subscription_path(GOOGLE_PROJECT, subscription_name),
            callback=generate_callback(Message, message_handler),
        )


def generate_callback(deserialiser, message_handler):
    def callback(message):
        deserialised_message = deserialiser(message)

        try:
            attributes = dict(message.attributes) if message.attributes else None
            if (
                "audience" in attributes
                and attributes["audience"]
                and APPLICATION_NAME not in attributes["audience"]
            ):
                message.ack()
                return

            message_handler(deserialised_message)

        except DropMessageException:
            message.ack()

    return callback
