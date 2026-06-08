import os
import pytest

@pytest.fixture(autouse=True)
def secure_test_env(monkeypatch):
    """
    Ensure all tests run in an isolated environment with dummy credentials.
    Prevents accidental leakage or usage of production secrets.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_test_gemini_api_key")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    yield
