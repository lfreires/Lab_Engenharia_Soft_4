from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "code": "validation_error"},
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": str(exc.args[0]), "code": "not_found"},
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": str(exc), "code": "forbidden"},
        )
