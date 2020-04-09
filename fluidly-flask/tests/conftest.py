import json

import pytest
from flask import Blueprint, Flask, Response

from fluidly.flask.api_exception import APIException, handle_api_exception
from fluidly.flask.decorators import admin, authorised
from fluidly.flask.exception_handling import log_safely

test_view = Blueprint("test_view", __name__)


@test_view.route("/authorised/<connection_id>")
@authorised
def authorised_endpoint(connection_id):
    return connection_id, 200


@test_view.route("/admin")
@admin
def admin_endpoint():
    return Response(
        response=json.dumps({"flaskStatus": "OK"}),
        status=200,
        mimetype="application/json",
    )


@test_view.route("/logging-success")
@log_safely
def logging_success_function():
    return Response(
        response=json.dumps({"flaskStatus": "OK"}),
        status=200,
        mimetype="application/json",
    )


@test_view.route("/logging-exception")
@log_safely
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
