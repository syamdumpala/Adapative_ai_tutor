"""Shared LLM access for graph nodes.

All agent nodes call `complete(stage, system, user)`. Tests monkeypatch this
single function (`app.features.tutor.graph.llm.complete`) so no real Claude call
is made.
"""

import json
import re
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.core.config import settings

_llm: ChatAnthropic | None = None


def _get_llm() -> ChatAnthropic:
    global _llm
    if _llm is None:
        kwargs: dict = {"model": settings.llm_model, "max_tokens": 1024, "timeout": 60}
        if settings.anthropic_api_key:
            kwargs["api_key"] = settings.anthropic_api_key
        _llm = ChatAnthropic(**kwargs)
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
    """Run one LLM completion. `stage` labels the agent (used by test mocks)."""
    resp = await _get_llm().ainvoke([SystemMessage(content=system), HumanMessage(content=user)])
    return _text(resp)


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
