from fluidly.structlog.pubsub_helper import pubsub_log_entrypoint


class Message:
    def __init__(self):
        self.attributes = {}
        self.data = {}


def test_pubsub_log_entrypoint():
    class TestClass:
        @pubsub_log_entrypoint
        def test_func(self, session, organisation):
            pass

    TestClass().test_func("session", Message())
