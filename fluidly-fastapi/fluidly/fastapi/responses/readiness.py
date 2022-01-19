from fastapi_camelcase import CamelModel # type: ignore

from fluidly.fastapi.constants.status import StatusEnum


class ReadinessResponse(CamelModel):
    fastapi_status: StatusEnum
