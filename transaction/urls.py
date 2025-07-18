from django.urls import path, include
from . import views



urlpatterns = [
    path('goals/', views.GoalViewSet.as_view({'get': 'list', 'post': 'create'}), name='goal-list-create'),
    path('goals/<int:pk>/', views.GoalViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='goal-detail'),
]


