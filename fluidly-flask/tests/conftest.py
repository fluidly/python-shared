import json

import pytest
from flask import Blueprint, Flask, Response
from fluidly.flask.api_exception import APIException
from fluidly.flask.rest_logger import rest_log_entrypoint

test_view = Blueprint("test_view", __name__)


@test_view.route("/logging-success")
@rest_log_entrypoint
def success():
    return Response(
        response=json.dumps({"flaskStatus": "OK"}),
        status=200,
        mimetype="application/json",
    )


@test_view.route("/logging-exception")
@rest_log_entrypoint
def exception():
    raise APIException(status=500, title="An Api Exception occurred.")


def create_app():
    API_PATH = "/shared"
    app = Flask(__name__)
    app.register_blueprint(test_view, url_prefix=API_PATH)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5000)


@pytest.fixture(scope="session")
def client():
    yield app.test_client()
