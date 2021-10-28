import pytest
import structlog

from fluidly.structlog.base_logger import (
    add_service_context,
    filter_by_level,
    get_logger,
)


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


def test_add_service_context_when_env_set(monkeypatch):
    monkeypatch.setenv("SERVICE_NAME", "fluidly-service")
    event = add_service_context(None, "some_method", {})

    assert event["serviceContext"]["service"] == "fluidly-service"


def test_add_service_context_does_nothing_when_not_env():
    event = add_service_context(None, "some_method", {})

    assert event == {}
