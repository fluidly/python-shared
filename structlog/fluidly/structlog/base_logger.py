import structlog
from structlog.threadlocal import wrap_dict

structlog.configure(
    processors=[
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=wrap_dict(dict),
)

get_logger = structlog.get_logger
