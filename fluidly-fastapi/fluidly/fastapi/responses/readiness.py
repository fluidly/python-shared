from fastapi_camelcase import CamelModel

from fluidly.fastapi.constants.status import StatusEnum


class ReadinessResponse(CamelModel):
    fastapi_status: StatusEnum
