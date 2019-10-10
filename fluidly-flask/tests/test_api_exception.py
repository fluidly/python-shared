from fluidly.flask.api_exception import APIException


def test_api_exception():
    try:
        raise APIException(
            title="Internal Server Error",
            status="500",
            detail="An internal server error occurred.",
        )
    except APIException as api_exception:
        assert api_exception.to_dict()["title"] == "Internal Server Error"
        assert api_exception.to_dict()["status"] == "500"
        assert api_exception.to_dict()["detail"] == "An internal server error occurred."
