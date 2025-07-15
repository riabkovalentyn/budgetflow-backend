from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, GoalViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    path('list/', views.TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('', include(router.urls)),
]


