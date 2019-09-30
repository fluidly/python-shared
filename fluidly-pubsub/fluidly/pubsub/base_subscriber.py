import os

from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")


def setup_base_subscriber(subscriptions):
    for subscription_name, generate_callback in subscriptions:
        subscribe_to_path(subscription_name, generate_callback)


def subscribe_to_path(subscription_name, generate_callback):
    subscriber.subscribe(
        subscriber.subscription_path(GOOGLE_PROJECT, subscription_name),
        callback=generate_callback,
    )
