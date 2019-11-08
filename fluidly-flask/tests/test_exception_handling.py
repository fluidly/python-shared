from fluidly.flask.exception_handling import handle_exceptions, log_safely  # noqa


def test_log_safely(client):
    response = client.get("/shared/logging-success")
    assert response.status_code == 200
