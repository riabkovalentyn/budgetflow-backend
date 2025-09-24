"""Health check endpoints.

- Liveness: always returns ok (process up)
- Readiness: checks MongoEngine connection by trying a lightweight call.
"""
from __future__ import annotations
from django.http import JsonResponse
from mongoengine.connection import get_connection


def health_live(_request):
    return JsonResponse({"status": "live"})


def health_ready(_request):
    try:
        # Ping Mongo via the underlying PyMongo client
        conn = get_connection()
        conn.admin.command('ping')
        mongo = "ok"
    except Exception as exc:  # pragma: no cover - defensive
        mongo = f"error: {exc.__class__.__name__}"  # keep it simple
    return JsonResponse({"status": "ready" if mongo == "ok" else "degraded", "mongo": mongo})
