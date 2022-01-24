from fluidly.fastapi.constants.status import StatusEnum
from fluidly.fastapi.responses.uptime import UptimeResponse


def test_uptime_response():
    UptimeResponse(fastapi_status=StatusEnum.OK)
