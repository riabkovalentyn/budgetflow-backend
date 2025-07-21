import pytest
from django.test import TestCase
from .models import Transaction

@pytest.fixture
def transaction():
    return Transaction.objects.create(
        title='Test transaction',
        amount=100,
        category='Test category',
        date='2023-03-01'
    )

def test_transaction_creation(transaction):
    assert transaction.title == 'Test transaction'
    assert transaction.amount == 100
    assert transaction.category == 'Test category'
    assert transaction.date == '2023-03-01'