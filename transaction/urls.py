from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.transactions import TransactionViewSet
from .views.goal import GoalViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'goals', GoalViewSet, basename='goal')


urlpatterns = [
    path('', include(router.urls)),
]


