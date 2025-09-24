import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_transactions_filters_and_pagination(monkeypatch):
    User = get_user_model()
    User.objects.create_user(
        username='f1', password='p1', email='f1@example.com'
    )
    client = APIClient()
    token_resp = client.post(
        '/api/token/',
        {'username': 'f1', 'password': 'p1'},
        format='json',
    )
    token = token_resp.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create a fake list of objects mimicking MongoEngine docs (only attrs used by serializer)
    class DummyTx:
        def __init__(self, _id, type_, amount, category, created_at):
            self.id = _id
            self.type = type_
            self.amount = amount
            self.category = category
            self.description = ''
            self.created_at = created_at

    from datetime import datetime, timedelta, timezone
    base = datetime.now(timezone.utc)
    fake = []
    for i in range(30):
        fake.append(
            DummyTx(
                str(i),
                'income' if i % 2 == 0 else 'expense',
                i * 10,
                'catA' if i % 3 == 0 else 'catB',
                base - timedelta(days=i),
            )
        )

    class FakeQS(list):
        def count(self_inner):  # noqa: N802
            return len(self_inner)

        def order_by(self_inner, *_args, **_kwargs):  # noqa: N802
            return self_inner

        def filter(self_inner, **_kw):  # no filtering here, handled earlier
            return self_inner

    fake_qs = FakeQS(fake)

    from transaction.views.transactions import TransactionViewSet
    monkeypatch.setattr(TransactionViewSet, 'get_queryset', lambda self: fake_qs)

    r = client.get('/api/transactions/?page=1&page_size=5')
    assert r.status_code == 200
    body = r.json()
    assert 'items' in body and len(body['items']) == 5
    assert 'pagination' in body and body['pagination']['total'] == 30


@pytest.mark.django_db
def test_transactions_summary(monkeypatch):
    User = get_user_model()
    User.objects.create_user(
        username='s1', password='p1', email='s1@example.com'
    )
    client = APIClient()
    token_resp = client.post(
        '/api/token/',
        {'username': 's1', 'password': 'p1'},
        format='json',
    )
    token = token_resp.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Monkeypatch summary to avoid Mongo dependency
    from transaction.services import TransactionService
    monkeypatch.setattr(TransactionService, 'user_summary', lambda user_id: {
        'totalIncome': 120.5,
        'totalExpense': 20.5,
        'net': 100.0,
    })

    r = client.get('/api/transactions/summary/')
    assert r.status_code == 200
    data = r.json()
    assert data['totalIncome'] == 120.5
    assert data['net'] == 100.0
