from django.urls import path, include
from . import views
from .views import TransactionListCreateView


urlpatterns = [
    path('list/', views.TransactionListCreateView.as_view(), name='transaction-list-create'),
]


