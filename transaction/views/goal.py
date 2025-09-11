from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Goal
from ..serializers import GoalSerializer


class GoalViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Goal.objects(user_id=user_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({'items': serializer.data})
        except Exception as exc:
                return Response({'detail': 'database_unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response({'id': str(instance.id)}, status=status.HTTP_201_CREATED)
        except Exception as exc:
                return Response({'detail': 'database_unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)