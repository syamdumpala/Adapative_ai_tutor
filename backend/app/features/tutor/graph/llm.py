"""Shared agent access for graph nodes.

Every LLM-backed node calls `run_agent(stage, schema, system, user)`. Under the
hood each agent is built with LangChain's `create_agent` (cached per system
prompt) over the provider-agnostic chat model from `app.core.llm`.

Output is restricted to JSON matching the agent's Pydantic `schema`:

* if the chat model supports structured output (API-key providers), the schema is
  passed to `create_agent` as `response_format` and enforced by the provider;
* otherwise (e.g. the dev-only Claude subscription model, which cannot bind
  tools), the schema is appended to the prompt at call time and the reply is
  parsed and validated back into it.

Either way `run_agent` returns a plain ``dict`` of the validated fields. Tests
monkeypatch this single function (`app.features.tutor.graph.llm.run_agent`) so no
real model call is made.
"""

import json
import re
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.llm import get_chat_model
from app.features.tutor.graph import trace

_llm: BaseChatModel | None = None
# create_agent instances are compiled once and reused, keyed by (stage, system).
_agents: dict[tuple[str, str], tuple[Any, bool]] = {}


def _get_llm() -> BaseChatModel:
    global _llm
    if _llm is None:
        _llm = get_chat_model()
    return _llm


def _supports_structured_output(model: BaseChatModel) -> bool:
    """True when the model overrides `bind_tools` (required for `response_format`).

    The Claude subscription model (dev) does not, so it takes the prompt+parse path.
    """
    return type(model).bind_tools is not BaseChatModel.bind_tools


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


def _schema_hint(schema: type[BaseModel]) -> str:
    """A compact 'reply with only this JSON shape' instruction for models that
    cannot enforce structured output natively. Appended at call time so the
    prompt files themselves stay untouched."""
    props = schema.model_json_schema().get("properties", {})
    shape = {name: spec.get("type", "string") for name, spec in props.items()}
    return (
        "\n\nReturn ONLY a valid JSON object with exactly these keys "
        f"(no markdown, no prose, no extra keys): {json.dumps(shape)}"
    )


def _validate(schema: type[BaseModel], data: dict[str, Any]) -> dict[str, Any]:
    """Coerce a parsed reply into the schema; fall back to defaults + whatever the
    model did provide, so a slightly-off reply never crashes a node."""
    try:
        return schema.model_validate(data).model_dump()
    except ValidationError:
        merged = schema().model_dump()
        if isinstance(data, dict):
            merged.update({k: v for k, v in data.items() if k in merged})
        return merged


def _get_agent(stage: str, system: str, schema: type[BaseModel]) -> tuple[Any, bool]:
    key = (stage, system)
    if key not in _agents:
        model = _get_llm()
        structured = _supports_structured_output(model)
        if structured:
            agent = create_agent(model, system_prompt=system, response_format=schema)
        else:
            agent = create_agent(model, system_prompt=system)
        _agents[key] = (agent, structured)
    return _agents[key]


async def run_agent(stage: str, schema: type[BaseModel], system: str, user: str) -> dict[str, Any]:
    """Run one agent and return its JSON output validated against `schema`.

    `stage` labels the agent for tracing (each run shows up as `agent:<stage>`).
    """
    agent, structured = _get_agent(stage, system, schema)
    user_prompt = user if structured else user + _schema_hint(schema)
    config = {
        "run_name": f"agent:{stage}",
        "tags": [f"agent:{stage}", f"provider:{settings.llm_provider}"],
        "metadata": {
            "agent": stage,
            "provider": settings.llm_provider,
            "model": settings.llm_model,
        },
    }
    result = await agent.ainvoke({"messages": [HumanMessage(content=user_prompt)]}, config=config)

    if structured:
        obj = result.get("structured_response")
        data = obj.model_dump() if isinstance(obj, BaseModel) else (obj or {})
        text = json.dumps(data)
    else:
        text = _text(result["messages"][-1])
        data = parse_json(text, {})

    validated = _validate(schema, data)
    trace.record(stage, {"system": system, "user": user}, text)
    return validated


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
