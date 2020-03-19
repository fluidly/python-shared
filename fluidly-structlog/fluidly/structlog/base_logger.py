from typing import Dict, Any

import structlog
from structlog.threadlocal import wrap_dict


def add_log_level_as_severity(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """
    Add the log level to the event dict.
    """
    if method_name == "warn":
        # The stdlib has an alias
        method_name = "warning"

    event_dict["severity"] = method_name
    return event_dict


structlog.configure(
    processors=[
        structlog.processors.format_exc_info,
        add_log_level_as_severity,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=wrap_dict(dict),
)

get_logger = structlog.get_logger
