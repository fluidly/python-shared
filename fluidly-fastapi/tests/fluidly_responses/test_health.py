from fluidly.fastapi.constants.status import StatusEnum
from fluidly.fastapi.responses.health import HealthResponse


def test_health_response():
    HealthResponse(fastapi_status=StatusEnum.OK)
