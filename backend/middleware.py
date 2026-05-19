import json
import logging
import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Configure root logger to output JSON to stdout (Azure Container Apps captures it)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ifmlogix")


def log(level: str, event: str, **kwargs):
    """Emit a structured JSON log line."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "event": event,
        **kwargs,
    }
    print(json.dumps(record, ensure_ascii=False))


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Try to read UID from state (set by auth dependency if called)
        uid = getattr(request.state, "uid", "anonymous")

        log(
            "INFO",
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            uid=uid,
        )
        return response
