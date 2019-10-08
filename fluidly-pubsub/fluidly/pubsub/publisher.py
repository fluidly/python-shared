from google.cloud.pubsub_v1 import PublisherClient

publisher = None


def get_pubsub_publisher():
    global publisher

    if publisher is None:
        publisher = PublisherClient()

    return publisher
