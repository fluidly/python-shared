from fluidly.timing import log_duration


def test_log_duration():
    with log_duration("test_event"):
        pass
