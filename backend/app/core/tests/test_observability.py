"""Unit tests for LangSmith observability wiring."""

import os

import pytest

from app.core.config import settings
from app.core.observability import configure_observability

# All vars configure_observability() may write.
_LANGSMITH_ENV = [
    "LANGSMITH_TRACING",
    "LANGCHAIN_TRACING_V2",
    "LANGSMITH_API_KEY",
    "LANGCHAIN_API_KEY",
    "LANGSMITH_PROJECT",
    "LANGCHAIN_PROJECT",
    "LANGSMITH_ENDPOINT",
    "LANGCHAIN_ENDPOINT",
]


@pytest.fixture(autouse=True)
def _isolate_env():
    """Snapshot and fully restore the LangSmith env around each test.

    configure_observability() writes os.environ directly, so we must restore it
    ourselves — otherwise enabling tracing here would leak into other tests and
    trigger real LangSmith network calls.
    """
    saved = {key: os.environ.get(key) for key in _LANGSMITH_ENV}
    for key in _LANGSMITH_ENV:
        os.environ.pop(key, None)
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_off_without_key(monkeypatch):
    # Auto mode (None) and no key -> off.
    monkeypatch.setattr(settings, "langsmith_tracing", None)
    monkeypatch.setattr(settings, "langsmith_api_key", None)
    assert configure_observability() is False
    assert "LANGSMITH_TRACING" not in os.environ


def test_explicit_false_forces_off_even_with_key(monkeypatch):
    monkeypatch.setattr(settings, "langsmith_tracing", False)
    monkeypatch.setattr(settings, "langsmith_api_key", "lsv2_test")
    assert configure_observability() is False
    assert "LANGSMITH_TRACING" not in os.environ


def test_flag_true_without_key_stays_off(monkeypatch):
    monkeypatch.setattr(settings, "langsmith_tracing", True)
    monkeypatch.setattr(settings, "langsmith_api_key", None)
    assert configure_observability() is False


def test_key_alone_auto_enables(monkeypatch):
    # The behavior the user asked for: a key in the env turns tracing on.
    monkeypatch.setattr(settings, "langsmith_tracing", None)
    monkeypatch.setattr(settings, "langsmith_api_key", "lsv2_test")
    monkeypatch.setattr(settings, "langsmith_project", "unit-test-project")

    assert configure_observability() is True
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "lsv2_test"
    assert os.environ["LANGSMITH_PROJECT"] == "unit-test-project"
