import json
from unittest.mock import Mock

import pytest
from flask import Flask, Response
from fluidly.flask.api_exception import APIException
from fluidly.generic_query import generic_query_views
from fluidly.generic_query.mock_model_factory import MockModel


@pytest.fixture(scope="session")
def mock_base():
    base_mock = Mock()
    values_mock = [MockModel()]

    base_mock._decl_class_registry.values.return_value = values_mock

    return base_mock


@pytest.fixture(scope="session")
def client(mock_base):
    app = create_app(mock_base)
    yield app.test_client()


def create_app(mock_base):
    API_PATH = "/"
    app = Flask(__name__)
    app.register_blueprint(
        generic_query_views.debug_connection_views(mock_base), url_prefix=API_PATH
    )

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        return Response(
            response=json.dumps(error.to_dict()),
            status=error.status,
            mimetype="application/problem+json",
        )

    return app
