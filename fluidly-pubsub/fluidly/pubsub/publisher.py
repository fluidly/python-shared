from typing import Optional

from google.cloud.pubsub_v1 import PublisherClient

publisher: Optional[PublisherClient] = None


def get_pubsub_publisher() -> PublisherClient:
    global publisher

    if publisher is None:
        publisher = PublisherClient()

    return publisher
