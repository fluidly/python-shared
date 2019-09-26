from base_logger import get_logger


def test_get_logger():
    assert get_logger() is not None
