from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Transaction
from ..serializers import TransactionSerializer


class TransactionViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Transaction.objects(user_id=user_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as exc:
            return Response({'detail': 'Database unavailable', 'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            out = self.get_serializer(instance)
            return Response(out.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'detail': 'Database unavailable', 'error': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

