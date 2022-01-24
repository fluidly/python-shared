from fastapi_camelcase import CamelModel

from fluidly.fastapi.constants.status import StatusEnum


class HealthResponse(CamelModel):
    fastapi_status: StatusEnum
