import json
from typing import Dict, Optional

from flask import Response


class APIException(Exception):
    def __init__(self, status: str, title: str, detail: Optional[str] = None):
        """While using APIException don't forget to register custom error
        handler:

            app.register_error_handler(APIException, handle_api_exception)
        """
        self.title = title
        self.status = status
        self.detail = detail

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {"title": self.title, "status": self.status, "detail": self.detail}


def handle_api_exception(error: APIException) -> Response:
    return Response(
        response=json.dumps(error.to_dict()),
        status=error.status,
        mimetype="application/problem+json",
    )
