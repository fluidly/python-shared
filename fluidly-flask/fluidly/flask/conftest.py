import json

import pytest
from flask import Blueprint, Flask, Response
from fluidly.flask.api_exception import APIException, handle_api_exception
from fluidly.flask.decorators import authorised
from fluidly.flask.rest_logger import rest_log_entrypoint

test_view = Blueprint("test_view", __name__)


@test_view.route("/authorised/<connection_id>")
@authorised
def authorised_endpoint(connection_id):
    return connection_id, 200


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
    app.register_error_handler(APIException, handle_api_exception)
    return app


app = create_app()


@pytest.fixture(scope="session")
def client():
    yield app.test_client()


@pytest.fixture(scope="session")
def flask_app(request):
    ctx = app.app_context()
    ctx.push()

    yield app.test_client()

    ctx.pop()
