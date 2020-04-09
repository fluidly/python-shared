from google.cloud import pubsub_v1

from fluidly.pubsub.base_subscriber import setup_base_subscriber

subscriber = pubsub_v1.SubscriberClient()


def setup_subscriptions(subscriptions):
    setup_base_subscriber(subscriber, subscriptions)
