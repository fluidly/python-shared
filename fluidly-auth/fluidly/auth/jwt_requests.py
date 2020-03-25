from typing import Any

import requests
from requests import Response


def make_jwt_request(signed_jwt: Any, url: Any) -> Response:
    """Makes an authorized request to the endpoint"""
    headers = {
        "Authorization": "Bearer {}".format(signed_jwt.decode("utf-8")),
        "content-type": "text/html",
    }

    response = requests.get(url, headers=headers)
    return response
