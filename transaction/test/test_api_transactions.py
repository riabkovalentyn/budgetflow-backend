import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_auth_and_list_transactions(monkeypatch):
    User = get_user_model()
    u = User.objects.create_user(username='t1', password='p1', email='t1@example.com')

    client = APIClient()
    resp = client.post('/api/token/', {'username': 't1', 'password': 'p1'}, format='json')
    assert resp.status_code == 200
    token = resp.data['access']

    def fake_objects(user_id=None):
        class Q(list):
            def order_by(self, *_):
                return self
        return Q()

    from transaction.views.transactions import TransactionViewSet
    monkeypatch.setattr(TransactionViewSet, 'get_queryset', lambda self: [])

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    r = client.get('/api/transactions/')
    assert r.status_code == 200
    assert r.json() == {'items': []}