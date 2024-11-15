import pytest


@pytest.fixture
def credential(monkeypatch):
    monkeypatch.setenv("SHODO_API_ROOT", "https://api.shodo.ink/@shodo/shodo/")
    monkeypatch.setenv("SHODO_API_TOKEN", "test-token")
