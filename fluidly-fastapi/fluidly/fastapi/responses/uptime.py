from fastapi_camelcase import CamelModel

from fluidly.fastapi.constants.status import StatusEnum


class UptimeResponse(CamelModel):
    fastapi_status: StatusEnum
