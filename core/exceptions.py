"""Custom DRF exception handler producing a consistent error format."""
from __future__ import annotations
from typing import Any
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def format_error(code: str, message: str, *, request=None, details: Any | None = None):
    payload = {
        "code": code,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    if request is not None and hasattr(request, 'request_id'):
        payload["request_id"] = getattr(request, 'request_id')
    return payload


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get('request')

    if response is None:
        # Unhandled
        data = format_error('internal_error', 'Internal server error', request=request)
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Standardize existing response data
    orig = response.data
    code = 'error'
    message = ''
    details = None

    if isinstance(orig, dict):
        # Common DRF error patterns
        message = orig.get('detail') or orig.get('message') or 'Error'
        details = {k: v for k, v in orig.items() if k not in {'detail', 'message'}} or None
    else:
        message = 'Error'
        details = orig

    response.data = format_error(code, message, request=request, details=details)
    return response
