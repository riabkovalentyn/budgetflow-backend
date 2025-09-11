from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.transactions import TransactionViewSet
from .views.goal import GoalViewSet
from .views.ai import AIAdviceView, AITranscribeView
from .views.bank import (
    BankProvidersView,
    BankConnectionsView,
    BankStartConnectView,
    BankDisconnectView,
    BankSyncNowView,
    BankScheduleView,
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'goals', GoalViewSet, basename='goal')


urlpatterns = [
    path('', include(router.urls)),
    # Allow GET for advice (frontend uses GET), route both GET and POST to same view
    path('ai/advice/', AIAdviceView.as_view(), name='ai-advice'),
    path('ai/transcribe/', AITranscribeView.as_view(), name='ai-transcribe'),
    # Bank endpoints
    path('bank/providers', BankProvidersView.as_view(), name='bank-providers'),
    path('bank/connections', BankConnectionsView.as_view(), name='bank-connections'),
    path('bank/connect', BankStartConnectView.as_view(), name='bank-connect'),
    path('bank/connections/<str:connection_id>/disconnect', BankDisconnectView.as_view(), name='bank-disconnect'),
    path('bank/connections/<str:connection_id>/sync', BankSyncNowView.as_view(), name='bank-sync-now'),
    path('bank/schedule', BankScheduleView.as_view(), name='bank-schedule'),
]


