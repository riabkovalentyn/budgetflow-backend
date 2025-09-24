"""Custom middleware: request ID injection and simple structured logging hooks."""
from __future__ import annotations
import uuid
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
REQUEST_ID_ATTR = "request_id"
RESPONSE_HEADER = "X-Request-ID"


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        rid = request.META.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        setattr(request, REQUEST_ID_ATTR, rid)
        request.request_start_ts = time.time()

    def process_response(self, request: HttpRequest, response: HttpResponse):
        rid = getattr(request, REQUEST_ID_ATTR, None)
        if rid:
            response[RESPONSE_HEADER] = rid
            # basic access log
            try:
                duration_ms = int(
                    (time.time() - getattr(request, 'request_start_ts', time.time())) * 1000
                )
                logger.info(
                    "request",
                    extra={
                        "event": "access",
                        "request_id": rid,
                        "method": request.method,
                        "path": request.path,
                        "status_code": getattr(response, 'status_code', 0),
                        "duration_ms": duration_ms,
                    },
                )
            except Exception:  # pragma: no cover - non-critical
                pass
        return response


class JSONErrorMiddleware(MiddlewareMixin):
    """Convert Django's default HTML 404/500 to API JSON when path starts with /api/.

    Runs late (should be placed after RequestIDMiddleware in stack) to inspect
    the generated response and wrap it if needed.
    """

    def process_response(self, request, response):  # noqa: D401
        try:
            path = getattr(request, 'path', '') or ''
            if not path.startswith('/api/'):
                return response
            content_type = response.get('Content-Type', '')
            if 'application/json' in content_type:
                return response
            status_code = getattr(response, 'status_code', 0)
            if status_code in (404, 500, 403):
                from .exceptions import format_error
                code_map = {404: 'not_found', 500: 'internal_error', 403: 'forbidden'}
                code = code_map.get(status_code, 'error')
                message = {
                    404: 'Not found',
                    500: 'Internal server error',
                    403: 'Forbidden',
                }.get(status_code, 'Error')
                payload = format_error(code, message, request=request)
                from django.http import JsonResponse
                return JsonResponse(payload, status=status_code)
        except Exception:  # pragma: no cover
            return response
        return response
