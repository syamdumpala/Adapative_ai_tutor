"""Shared LLM access for graph nodes.

All agent nodes call `complete(stage, system, user)`. The underlying chat model is
built by the provider factory in `app.core.llm` (selected by LLM_PROVIDER /
LLM_AUTH_MODE / LLM_MODEL), so the nodes are provider-agnostic. Tests monkeypatch
this single function (`app.features.tutor.graph.llm.complete`) so no real call is made.
"""

import json
import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.core.config import settings
from app.core.llm import get_chat_model
from app.features.tutor.graph import trace

_llm: BaseChatModel | None = None


def _get_llm() -> BaseChatModel:
    global _llm
    if _llm is None:
        _llm = get_chat_model()
    return _llm


def _text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content.strip()
    parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "".join(parts).strip()


async def complete(stage: str, system: str, user: str) -> str:
    """Run one LLM completion. `stage` labels the agent (used by test mocks and by
    LangSmith tracing — each call shows up as `agent:<stage>` with model metadata)."""
    resp = await _get_llm().ainvoke(
        [SystemMessage(content=system), HumanMessage(content=user)],
        config={
            "run_name": f"agent:{stage}",
            "tags": [f"agent:{stage}", f"provider:{settings.llm_provider}"],
            "metadata": {
                "agent": stage,
                "provider": settings.llm_provider,
                "model": settings.llm_model,
            },
        },
    )
    text = _text(resp)
    trace.record(stage, {"system": system, "user": user}, text)
    return text


def parse_json(text: str, default: dict[str, Any]) -> dict[str, Any]:
    """Best-effort JSON parse; falls back to `default` if the text isn't valid JSON."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return default
