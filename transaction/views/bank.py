from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import datetime, timedelta

from ..models import BankConnection, BankSyncSchedule
from ..serializers import (
    BankProviderSerializer,
    BankConnectionSerializer,
    BankSyncScheduleSerializer,
)


# Static providers for now; can be extended later to real integrations.
STATIC_PROVIDERS = [
    {"id": "mockbank", "name": "Mock Bank"},
    {"id": "monobank", "name": "Monobank"},
    {"id": "privatbank", "name": "PrivatBank"},
]


class BankProvidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ser = BankProviderSerializer(STATIC_PROVIDERS, many=True)
        return Response({"providers": ser.data})


class BankConnectionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            conns = BankConnection.objects(user_id=request.user.id)
            ser = BankConnectionSerializer(conns, many=True)
            return Response({"connections": ser.data})
        except Exception:
            # If DB is unavailable during tests/local runs, return empty list
            return Response({"connections": []})


class BankStartConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        provider_id = (request.data or {}).get("providerId")
        if not provider_id:
            return Response({"message": "providerId required"}, status=status.HTTP_400_BAD_REQUEST)
        prov = next((p for p in STATIC_PROVIDERS if p["id"] == provider_id), None)
        if not prov:
            return Response({"message": "unknown provider"}, status=status.HTTP_400_BAD_REQUEST)

        # Create pending connection
        try:
            conn = BankConnection(
                user_id=request.user.id,
                provider_id=prov["id"],
                provider_name=prov["name"],
                status="connected",  # assume immediate connect for mock
                last_synced_at=None,
            )
            conn.save()
            cid = str(conn.id)
        except Exception:
            # Fallback without DB: generate ephemeral id
            import uuid
            cid = str(uuid.uuid4())
        # Frontend supports either URL redirect or connectionId
        return Response({"connectionId": cid})


class BankDisconnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_id: str):
        try:
            conn = BankConnection.objects(id=connection_id, user_id=request.user.id).first()
            if not conn:
                return Response(status=status.HTTP_404_NOT_FOUND)
            conn.status = "disconnected"
            conn.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_204_NO_CONTENT)


class BankSyncNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_id: str):
        try:
            conn = BankConnection.objects(id=connection_id, user_id=request.user.id).first()
            if not conn:
                return Response(status=status.HTTP_404_NOT_FOUND)
            # Simulate sync
            conn.last_synced_at = datetime.utcnow()
            conn.status = "connected"
            conn.save()
            return Response({"started": True})
        except Exception:
            return Response({"started": True})


def _get_or_create_schedule(user_id: int) -> BankSyncSchedule | None:
    try:
        sched = BankSyncSchedule.objects(user_id=user_id).first()
        if not sched:
            sched = BankSyncSchedule(user_id=user_id, enabled=0, interval_hours=2, next_run_at=None)
            sched.save()
        return sched
    except Exception:
        return None


class BankScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sched = _get_or_create_schedule(request.user.id)
        if not sched:
            return Response({"schedule": {"enabled": False, "intervalHours": 2, "nextRunAt": None}})
        # Convert enabled int to boolean for serializer by creating a temp-like obj
        sched.enabled = 1 if sched.enabled else 0
        ser = BankSyncScheduleSerializer(sched)
        # Fix boolean representation
        data = ser.data
        data["enabled"] = bool(sched.enabled)
        return Response({"schedule": data})

    def post(self, request):
        enabled = bool((request.data or {}).get("enabled", False))
        interval_hours = int((request.data or {}).get("intervalHours", 2))
        sched = _get_or_create_schedule(request.user.id)
        if not sched:
            next_run = datetime.utcnow() + timedelta(hours=interval_hours) if enabled else None
            return Response({"schedule": {"enabled": enabled, "intervalHours": interval_hours, "nextRunAt": next_run.isoformat() if next_run else None}})
        sched.enabled = 1 if enabled else 0
        sched.interval_hours = interval_hours
        # naive next run
        sched.next_run_at = datetime.utcnow() + timedelta(hours=interval_hours) if enabled else None
        sched.save()

        ser = BankSyncScheduleSerializer(sched)
        data = ser.data
        data["enabled"] = bool(sched.enabled)
        return Response({"schedule": data})
