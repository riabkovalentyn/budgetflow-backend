import pytest
from fastapi.testclient import TestClient
from ai_service.app import app


@pytest.fixture(autouse=True)
def _disable_openai(monkeypatch):
    monkeypatch.setenv('AI_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', '')


def test_advice_disabled():
    client = TestClient(app)
    body = {"transactions": [], "prompt": "hello"}
    r = client.post('/advice', json=body)
    assert r.status_code == 200
    assert r.json().get('advice') in ("AI disabled", "AI error")


def test_transcribe_disabled():
    client = TestClient(app)
    files = {'audio': ('x.wav', b'123', 'audio/wav')}
    r = client.post('/transcribe', files=files)
    assert r.status_code == 200
    assert r.json().get('text') in ("AI disabled", "AI error")
