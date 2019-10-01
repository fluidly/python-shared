import os

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT")


def setup_base_subscriber(subscriber, subscriptions):
    for subscription_name, generate_callback in subscriptions:
        subscriber.subscribe(
            subscriber.subscription_path(GOOGLE_PROJECT, subscription_name),
            callback=generate_callback,
        )
