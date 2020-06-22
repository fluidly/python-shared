from typing import Optional

from flask import Response, request

from fluidly.structlog.base_logger import get_logger

WILDCARD_ACCEPT_HEADER = "*/*"


def is_valid_content_type(
    accept_header: str, response_content_type: Optional[str]
) -> bool:
    return (
        accept_header == WILDCARD_ACCEPT_HEADER
        or accept_header == response_content_type
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
            args=dict(request.view_args),
            headers=dict(headers),
            url=request.full_path,
            request_accept_header=accept_header,
            response_content_type=response.content_type,
        )

    return response
