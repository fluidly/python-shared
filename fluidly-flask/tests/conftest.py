import pytest
import json
from flask import Flask, Blueprint, Response, jsonify
from fluidly.flask.rest_logger import rest_log_entrypoint
from fluidly.flask.api_exception import APIException


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
    raise APIException()


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

