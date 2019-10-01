from fluidly.pubsub.base_subscriber import setup_base_subscriber
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()

# Take in a tuple list: first item the subscription name as a string, and second is function that accepts a message
def setup_subscriptions(subscriptions):
    setup_base_subscriber(subscriber, subscriptions)
