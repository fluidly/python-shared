from google.cloud import pubsub_v1

from fluidly.pubsub.base_subscriber import Subscriptions, setup_base_subscriber

subscriber = pubsub_v1.SubscriberClient()


def setup_subscriptions(subscriptions: Subscriptions) -> None:
    setup_base_subscriber(subscriber, subscriptions)
