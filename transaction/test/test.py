import pytest
from django.test import TestCase
from .models import Transaction, Goal

@pytest.mark.django_db
def test_transaction_creation():
    transaction = Transaction.objects.create(
        title='Test transaction',
        amount=100,
        category='Test category',
        date='2023-03-01'
    )
    assert transaction.title == 'Test transaction'
    assert transaction.amount == 100
    assert transaction.category == 'Test category'
    assert transaction.date == '2023-03-01'

@pytest.mark.django_db
def test_goal_creation():
    goal = Goal.objects.create(
        title='Test goal',
        amount=1000,
        category='Test category'
    )
    assert goal.title == 'Test goal'
    assert goal.amount == 1000
    assert goal.category == 'Test category'