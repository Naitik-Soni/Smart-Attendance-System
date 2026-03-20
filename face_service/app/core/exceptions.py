from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class FaceException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(FaceException)
    async def face_exception_handler(request: Request, exc: FaceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "code": exc.code, "message": exc.message, "errors": []}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "errors": [],
            },
        )
