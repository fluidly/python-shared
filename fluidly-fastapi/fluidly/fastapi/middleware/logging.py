import time
from typing import Any

from fastapi.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from fluidly.structlog.base_logger import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    JSON_PROBLEM_CONTENT_TYPE = "application/problem+json"

    @staticmethod
    def _override_content_type(response: Response) -> None:
        response.headers["content-type"] = LoggingMiddleware.JSON_PROBLEM_CONTENT_TYPE

    @staticmethod
    def _bind_request_context(logger: Any, request: Request) -> None:
        # todo: think of a way to get at least few of these before invoking `call_next`
        # https://github.com/tiangolo/fastapi/issues/1879#issuecomment-672684259

        endpoint = request.scope.get("endpoint")
        endpoint_name = getattr(endpoint, "__qualname__", None)

        logger.bind(
            url=str(request.url),
            args=request.path_params,
            connection_id=request.path_params.get("connection_id"),
            partner_id=request.path_params.get("partner_id"),
            headers=dict(request.headers),
            callback=endpoint_name,
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger = get_logger()
        start = time.time()

        try:
            response = await call_next(request)
            self._bind_request_context(logger, request)

            if response.status_code >= 400:
                # Error handlers in FastAPI turn raised exceptions into Response objects.
                # They are invoked before middlewares, thus we cannot catch `HTTPException` in here
                # Maybe we should try creating custom APIRouter instead of using middleware:
                # https://github.com/tiangolo/fastapi/issues/954#issuecomment-617683548

                self._override_content_type(response)

                end = time.time()
                logger.error(
                    "rest_request_processed",
                    duration=end - start,
                    success=False,
                    status_code=response.status_code,
                )

                return response

        except Exception:
            self._bind_request_context(logger, request)
            end = time.time()
            logger.error(
                "rest_request_processed",
                duration=end - start,
                success=False,
                exc_info=True,
                status_code=500,
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "An unknown error occurred"},
                media_type=LoggingMiddleware.JSON_PROBLEM_CONTENT_TYPE,
            )

        end = time.time()
        logger.info(
            "rest_request_processed",
            duration=end - start,
            success=True,
            status_code=response.status_code,
        )
        return response
