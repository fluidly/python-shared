import logging
import os
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.threadlocal import wrap_dict


def filter_by_level(
    logger: Any, method_name: str, event_dict: Dict, min_level: Optional[str] = None
) -> Dict:
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


def add_log_level_as_severity(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """
    Add the log level to the event dict.
    """
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"

    event_dict["severity"] = method_name
    return event_dict


def add_service_context(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Add serviceContext.service if the env variable SERVICE_NAME is set for error reporting in gcp"""
    service_name = os.getenv("SERVICE_NAME")
    if service_name:
        event_dict["serviceContext"] = {"service": service_name}
    return event_dict


structlog.configure(
    processors=[
        filter_by_level,
        structlog.processors.format_exc_info,
        add_log_level_as_severity,
        add_service_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if "PRETTY_LOGS" in os.environ
        else structlog.processors.JSONRenderer(),
    ],
    context_class=wrap_dict(dict),
)

get_logger = structlog.get_logger


def unhandeld_exception_hook(exception_type, exception, traceback):
    logger = get_logger()
    logger.exception(
        "Unhandeld Exception", exc_info=(exception_type, exception, traceback)
    )


def setup_logging():
    """Add a sys.excepthook so that the log processors are applied and there is nice
    error log in gcp"""
    sys.excepthook = unhandeld_exception_hook
