import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_live_and_ready():
    client = APIClient()
    r_live = client.get('/health/live')
    assert r_live.status_code == 200
    assert r_live.json()['status'] == 'live'

    r_ready = client.get('/health/ready')
    assert r_ready.status_code == 200
    body = r_ready.json()
    assert 'status' in body and 'mongo' in body


def test_error_format_404():
    client = APIClient()
    r = client.get('/api/unknown-endpoint-zzz/')
    # Should be standardized by custom exception handler
    assert r.status_code == 404
    data = r.json()
    assert set(['code', 'message']).issubset(data.keys())
