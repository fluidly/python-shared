import pytest
import structlog

from fluidly.structlog.base_logger import get_logger, filter_by_level


def test_get_logger():
    logger = get_logger()
    assert logger is not None
    logger.info("test logger")


def test_filter_by_level():
    logger = object()  # doesn't matter
    message = {"key": "value"}

    with pytest.raises(structlog.DropEvent):
        filter_by_level(logger, "debug", message)
        filter_by_level(logger, "info", message)

    assert filter_by_level(logger, "warn", message)
    assert filter_by_level(logger, "warning", message)
    assert filter_by_level(logger, "error", message)
    assert filter_by_level(logger, "critical", message)


def test_filter_by_level_with_unknown_method():
    assert filter_by_level(object(), "foo", {"key": "value"})  # not dropped
