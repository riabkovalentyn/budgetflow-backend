import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_bank_providers_and_connections(monkeypatch):
    User = get_user_model()
    User.objects.create_user(username='t2', password='p2', email='t2@example.com')
    client = APIClient()
    resp = client.post('/api/token/', {'username': 't2', 'password': 'p2'}, format='json')
    assert resp.status_code == 200
    token = resp.data['access']

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    r = client.get('/api/bank/providers')
    assert r.status_code == 200
    assert 'providers' in r.json()

    # Start connect
    pid = r.json()['providers'][0]['id']
    rc = client.post('/api/bank/connect', {'providerId': pid}, format='json')
    assert rc.status_code == 200
    assert 'connectionId' in rc.json()

    # List connections
    rlist = client.get('/api/bank/connections')
    assert rlist.status_code == 200
    assert 'connections' in rlist.json()
