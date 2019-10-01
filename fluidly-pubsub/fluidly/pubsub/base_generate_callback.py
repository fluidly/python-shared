import os

from fluidly.pubsub.exceptions import DropMessageException
from fluidly.pubsub.message import Message
from sqlalchemy.exc import IntegrityError

APPLICATION_NAME = os.getenv("APPLICATION_NAME")


def base_generate_callback(message_handler):
    def callback(message):
        deserialised_message = Message(message)

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
        except IntegrityError:
            # If an IntegrityError is raised (typically a UniqueViolation exception)
            # then we want to acknowledge the message but still raise the exception.
            # This means we know about it but not block the subscription.
            message.ack()
            raise

    return callback
