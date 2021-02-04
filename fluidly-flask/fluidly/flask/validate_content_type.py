from typing import Optional

from flask import Response, request

from fluidly.structlog.base_logger import get_logger

WILDCARD_ACCEPT_HEADER = "*/*"


def extract_root_type(content_type: Optional[str]) -> Optional[str]:
    """Examples of subset content types are:

    application/problem+json
    image/svg+xml
    """
    if not content_type:
        return content_type

    try:
        prefix, suffix = content_type.split("/", 1)
        _, base_suffix = suffix.rsplit("+", 1)
    except Exception:
        # If any exception occurs, do not prevent the response from returning
        return content_type

    return f"{prefix}/{base_suffix}"


def is_valid_content_type(
    accept_header: str, response_content_type: Optional[str]
) -> bool:
    return (
        accept_header == WILDCARD_ACCEPT_HEADER
        or accept_header == response_content_type
        or accept_header == extract_root_type(response_content_type)
    )


def validate_content_type(response: Response) -> Response:
    """Checks if the response content-type is compatible with the request's
    Accept header. If a mismatch is found, log the request.

    Use with flask.after_request hook i.e.

        app.after_request(validate_content_type)

    Note: this currently does very basic validation to cover the common cases.
    It does not support multiple mimetypes or wildcard subtypes (for now).

    If an exception is raised during the request, after_request hooks are not run.
    """
    headers = request.headers
    accept_header = headers.get("Accept", WILDCARD_ACCEPT_HEADER)

    accept_headers = accept_header.split(",")

    if not any(is_valid_content_type(h, response.content_type) for h in accept_headers):
        logger = get_logger()

        logger.warning(
            "Incompatible request Accept header and response content-type",
            args=dict(request.view_args) if request.view_args is not None else None,
            headers=dict(headers),
            url=request.full_path,
            request_accept_header=accept_header,
            response_content_type=response.content_type,
        )

    return response
