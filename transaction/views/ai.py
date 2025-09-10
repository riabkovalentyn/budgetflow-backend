from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
import requests
import json


class AIAdviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.AI_FEATURES_ENABLED:
            return Response({'detail': 'ai_disabled'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            user_id = request.user.id
            from ..models import Transaction as Tx
            txs = list(Tx.objects(user_id=user_id).order_by('-created_at')[:50])
            payload = {
                'transactions': [
                    {
                        'type': t.type,
                        'amount': float(t.amount),
                        'category': t.category,
                        'description': getattr(t, 'description', ''),
                        'created_at': t.created_at.isoformat() if getattr(t, 'created_at', None) else None,
                    }
                    for t in txs
                ],
                'prompt': request.data.get('prompt') or ''
            }
        except Exception:
            return Response({'detail': 'database_unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            url = settings.AI_SERVICE_URL.rstrip('/') + '/advice'
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code != 200:
                return Response({'detail': 'ai_error'}, status=status.HTTP_502_BAD_GATEWAY)
            return Response(r.json(), status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'ai_unreachable'}, status=status.HTTP_502_BAD_GATEWAY)


class AITranscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.AI_FEATURES_ENABLED:
            return Response({'detail': 'ai_disabled'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        audio = request.FILES.get('audio')
        if not audio:
            return Response({'detail': 'audio_required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            url = settings.AI_SERVICE_URL.rstrip('/') + '/transcribe'
            files = {'audio': (audio.name, audio.read(), audio.content_type or 'application/octet-stream')}
            r = requests.post(url, files=files, timeout=120)
            if r.status_code != 200:
                return Response({'detail': 'ai_error'}, status=status.HTTP_502_BAD_GATEWAY)
            return Response(r.json(), status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'ai_unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
