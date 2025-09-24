from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import GoalSerializer
from ..services import GoalService


class GoalViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return GoalService.list_user_goals(user_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({'items': serializer.data})
        except Exception:
            return Response(
                {'detail': 'database_unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            instance = GoalService.create_goal(
                user_id=request.user.id,
                title=data['title'],
                target_amount=data.get('target_amount'),
                current_amount=data.get('current_amount'),
                due_date=data.get('due_date'),
                description=data.get('description') or '',
                image=data.get('image') or '/vercel.svg',
            )
            return Response({'id': str(instance.id)}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {'detail': 'database_unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
