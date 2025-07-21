import pytest
from django.test import TestCase
from .models import Goal

@pytest.fixture
def goal():
    return Goal.objects.create(
        title='Test goal',
        amount=1000,
        category='Test category'
    )

def test_goal_creation(goal):
    assert goal.title == 'Test goal'
    assert goal.amount == 1000
    assert goal.category == 'Test category'