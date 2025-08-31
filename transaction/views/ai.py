from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
import json


class AIAdviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.AI_FEATURES_ENABLED or settings.AI_PROVIDER != 'openai' or not settings.OPENAI_API_KEY:
            return Response({'detail': 'AI is disabled'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Collect last N transactions for context
        try:
            user_id = request.user.id
            from ..models import Transaction as Tx
            txs = list(Tx.objects(user_id=user_id).order_by('-created_at')[:50])
            transactions = [
                {
                    'type': t.type,
                    'amount': float(t.amount),
                    'category': t.category,
                    'description': getattr(t, 'description', ''),
                    'created_at': t.created_at.isoformat() if getattr(t, 'created_at', None) else None,
                }
                for t in txs
            ]
        except Exception as exc:
            return Response({'detail': 'Database unavailable', 'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Build prompt
        goals = []  # later: load from DB
        user_prompt = request.data.get('prompt', 'Give me budget advice based on my recent transactions.')
        system = (
            'You are a financial assistant. Analyze the provided transactions and provide 3-5 concise, practical '
            'recommendations tailored to saving/budgeting. Be specific and numeric when possible.'
        )
        content = json.dumps({'transactions': transactions, 'goals': goals, 'user_prompt': user_prompt})

        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': content},
                ],
                temperature=0.4,
            )
            advice = completion.choices[0].message.content
            return Response({'advice': advice}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'detail': 'AI provider error', 'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class AITranscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Accept a multipart/form-data file field 'audio' and return transcription text."""
        if not settings.AI_FEATURES_ENABLED or settings.AI_PROVIDER != 'openai' or not settings.OPENAI_API_KEY:
            return Response({'detail': 'AI is disabled'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        audio = request.FILES.get('audio')
        if not audio:
            return Response({'detail': 'audio file required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            # Whisper via audio.transcriptions
            result = client.audio.transcriptions.create(
                model='whisper-1',
                file=audio,
            )
            text = getattr(result, 'text', None) or getattr(result, 'data', None) or ''
            return Response({'text': text}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'detail': 'AI provider error', 'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
