import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from middleware import log


async def global_exception_handler(request: Request, exc: Exception):
    """Return generic error to client; log full detail server-side."""
    log(
        "ERROR",
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_detail=str(exc),
        traceback=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error"},
    )
