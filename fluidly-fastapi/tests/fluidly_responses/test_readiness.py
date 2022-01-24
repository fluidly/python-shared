from fluidly.fastapi.constants.status import StatusEnum
from fluidly.fastapi.responses.readiness import ReadinessResponse


def test_readiness_response():
    ReadinessResponse(fastapi_status=StatusEnum.OK)
