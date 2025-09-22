import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_and_me():
    client = APIClient()
    r = client.post('/api/auth/register', {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'secret123',
    }, format='json')
    assert r.status_code == 201, r.content
    data = r.json()
    assert 'access' in data and 'refresh' in data
    assert data['user']['username'] == 'newuser'

    token = data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    me = client.get('/api/auth/me')
    assert me.status_code == 200
    j = me.json()
    assert j['username'] == 'newuser'
