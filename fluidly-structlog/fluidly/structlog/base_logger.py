import logging
import os
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.threadlocal import wrap_dict

Logger = Any
EventDict = Dict[str, Any]


def filter_by_level(
    logger: Logger,
    method_name: str,
    event_dict: EventDict,
    min_level: Optional[str] = None,
) -> EventDict:
    """Filter out log messages lower than specified level.

    Default minimum level is LOG_LEVEL environment variable or if unset INFO.
    """
    if min_level is None:
        min_level = os.getenv("LOG_LEVEL", "INFO").upper()

    level = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }  # type: Dict[str, int]
    try:
        if level[method_name.upper()] < level[min_level]:
            raise structlog.DropEvent
    except KeyError:
        pass  # always return message if logger method or LOG_LEVEL is non-standard
    return event_dict


def add_log_level_as_severity(
    logger: Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Add the log level to the event dict.
    """
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"

    event_dict["severity"] = method_name
    return event_dict


def add_service_context(
    logger: Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add serviceContext.service if the env variable APPLICATION_NAME is set for error reporting in gcp"""
    service_name = os.getenv("APPLICATION_NAME")
    if service_name:
        event_dict["serviceContext"] = {"service": service_name}
    return event_dict


def unhandled_exception_hook(
    exception_type: Any, exception: Any, traceback: Any
) -> None:
    """Hook to make sure the log processors are applied to unhandled exceptions as well"""
    logger = get_logger()
    logger.exception(
        "Unhandled Exception", exc_info=(exception_type, exception, traceback)
    )


def get_logger() -> Logger:
    if not structlog.is_configured():
        structlog.configure(
            processors=[
                filter_by_level,  # type: ignore
                structlog.processors.format_exc_info,
                add_log_level_as_severity,  # type: ignore
                add_service_context,  # type: ignore
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer()  # type: ignore
                if "PRETTY_LOGS" in os.environ
                else structlog.processors.JSONRenderer(),
            ],
            context_class=wrap_dict(dict),
        )
        sys.excepthook = unhandled_exception_hook  # Overriding the default excepthook for better logging of unhandled exceptions
    return structlog.get_logger()
