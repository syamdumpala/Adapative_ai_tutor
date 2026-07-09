"""Unit tests for the LLM provider factory (`app/core/llm.py`).

These exercise the pure configuration gates and the local (OpenAI-compatible)
builder without any network call or real credentials — constructing a
``ChatOpenAI`` does not contact the server.
"""

import pytest

from app.core import llm
from app.core.config import settings


@pytest.fixture
def local_settings(monkeypatch):
    """Configure the process to target a local OpenAI-compatible server."""
    monkeypatch.setattr(settings, "llm_provider", "local")
    monkeypatch.setattr(settings, "llm_model", "local-model")
    monkeypatch.setattr(settings, "local_base_url", "http://localhost:1234/v1")
    monkeypatch.setattr(settings, "local_api_key", "not-needed")


def test_local_is_configured_when_base_url_set(local_settings):
    assert llm.llm_is_configured() is True


def test_local_not_configured_without_base_url(monkeypatch, local_settings):
    monkeypatch.setattr(settings, "local_base_url", None)
    assert llm.llm_is_configured() is False
    assert "LOCAL_BASE_URL" in llm.llm_config_detail()


def test_get_chat_model_builds_openai_client_for_local(local_settings):
    model = llm.get_chat_model()
    assert type(model).__name__ == "ChatOpenAI"


def test_local_build_raises_without_base_url(monkeypatch, local_settings):
    monkeypatch.setattr(settings, "local_base_url", None)
    with pytest.raises(llm.LLMConfigError):
        llm.get_chat_model()


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "bogus")
    with pytest.raises(llm.LLMConfigError):
        llm.get_chat_model()
