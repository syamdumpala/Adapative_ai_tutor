"""LLM provider factory.

The tutoring pipeline builds its chat model through :func:`get_chat_model`, which
selects a backend purely from configuration so the same code runs across
environments without edits:

* **Development** — route calls through a Claude Pro/Max *subscription* using the
  Claude Agent SDK (reads ``CLAUDE_CODE_OAUTH_TOKEN``), so no metered API tokens
  are spent. Set ``LLM_PROVIDER=anthropic`` + ``LLM_AUTH_MODE=subscription``.
* **Production** — a first-party API key for Anthropic, OpenAI, or Google Gemini,
  selected by ``LLM_PROVIDER`` (``LLM_AUTH_MODE`` is ignored for openai/google).
* **Local** — an OpenAI-compatible model server (LM Studio, Ollama, vLLM,
  llama.cpp, …). Set ``LLM_PROVIDER=local`` + ``LOCAL_BASE_URL`` (e.g.
  ``http://localhost:1234/v1``); reuses the OpenAI client, so no extra dependency.

The model id is always ``LLM_MODEL`` and applies in subscription mode too, so the
same token can address ``claude-sonnet-5`` or ``claude-opus-4-8`` per requirement.
The returned object is always a LangChain :class:`BaseChatModel`, so the pipeline
nodes (``.ainvoke(...)``) never change.

Subscription mode is **development-only**: a Claude subscription does not include
API access, and the OAuth token is licensed for individual use through Claude Code
and the Agent SDK — never ship it in a multi-user/staging backend. Production uses
an API-key provider, which is the ToS-clean, multi-user-safe path.

Provider packages are imported lazily, so an environment only needs the package for
the provider it actually selects (`claude-agent-sdk` for dev; `langchain-openai` /
`langchain-google-genai` for prod).
"""

from __future__ import annotations

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.core.config import settings

_MAX_TOKENS = 2048
_TIMEOUT = 60


class LLMConfigError(RuntimeError):
    """The selected provider is missing a required credential or dependency."""


def _provider() -> str:
    return (settings.llm_provider or "anthropic").strip().lower()


def _auth_mode() -> str:
    return (settings.llm_auth_mode or "subscription").strip().lower()


def llm_is_configured() -> bool:
    """Whether the selected provider has the credentials it needs to run."""
    provider = _provider()
    if provider == "anthropic":
        if _auth_mode() == "subscription":
            return bool(settings.claude_code_oauth_token)
        return bool(settings.anthropic_api_key)
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "google":
        return bool(settings.google_api_key)
    if provider == "local":
        return bool(settings.local_base_url)
    return False


def llm_config_detail() -> str:
    """Human-readable reason the LLM is unconfigured (for the 503 response body)."""
    provider = _provider()
    if provider == "anthropic" and _auth_mode() == "subscription":
        return "CLAUDE_CODE_OAUTH_TOKEN is not set (LLM_AUTH_MODE=subscription)"
    if provider == "local":
        return "LOCAL_BASE_URL is not set (LLM_PROVIDER=local), e.g. http://localhost:1234/v1"
    env_key = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
    }.get(provider)
    if env_key:
        return f"{env_key} is not set (LLM_PROVIDER={provider})"
    return f"Unknown LLM_PROVIDER={provider!r}; expected anthropic | openai | google"


def get_chat_model(model: str | None = None) -> BaseChatModel:
    """Build the configured chat model. ``model`` overrides ``LLM_MODEL`` when given."""
    provider = _provider()
    model = model or settings.llm_model or None
    if provider == "anthropic":
        if _auth_mode() == "subscription":
            return _build_subscription(model)
        return _build_anthropic(model)
    if provider == "openai":
        return _build_openai(model)
    if provider == "google":
        return _build_google(model)
    if provider == "local":
        return _build_local(model)
    raise LLMConfigError(
        f"Unknown LLM_PROVIDER={provider!r}; expected anthropic | openai | google | local"
    )


def _build_anthropic(model: str | None) -> BaseChatModel:
    if not settings.anthropic_api_key:
        raise LLMConfigError("ANTHROPIC_API_KEY is not set (LLM_AUTH_MODE=api_key)")
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=model,
        api_key=settings.anthropic_api_key,
        max_tokens=_MAX_TOKENS,
        timeout=_TIMEOUT,
        effort=0,  # default is 0.5; 0.0 = faster, 1.0 = more accurate
    )


def _build_openai(model: str | None) -> BaseChatModel:
    if not settings.openai_api_key:
        raise LLMConfigError("OPENAI_API_KEY is not set (LLM_PROVIDER=openai)")
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model or "gpt-4o",
        api_key=settings.openai_api_key,
        max_tokens=_MAX_TOKENS,
        timeout=_TIMEOUT,
    )


def _build_local(model: str | None) -> BaseChatModel:
    """Talk to a local OpenAI-compatible server (LM Studio / Ollama / vLLM / …).

    These runtimes all expose ``/v1/chat/completions``, so we reuse the OpenAI
    client (already a dependency) with ``base_url`` pointed at the local server and
    a placeholder key — no local runtime validates it.
    """
    if not settings.local_base_url:
        raise LLMConfigError(
            "LOCAL_BASE_URL is not set (LLM_PROVIDER=local), e.g. http://localhost:1234/v1"
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model or "local-model",
        base_url=settings.local_base_url,
        api_key=settings.local_api_key or "not-needed",
        max_tokens=_MAX_TOKENS,
        timeout=_TIMEOUT,
    )


def _build_google(model: str | None) -> BaseChatModel:
    if not settings.google_api_key:
        raise LLMConfigError("GOOGLE_API_KEY is not set (LLM_PROVIDER=google)")
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model or "gemini-2.5-pro",
        google_api_key=settings.google_api_key,
        max_output_tokens=_MAX_TOKENS,
        timeout=_TIMEOUT,
    )


def _build_subscription(model: str | None) -> BaseChatModel:
    if not settings.claude_code_oauth_token:
        raise LLMConfigError(
            "CLAUDE_CODE_OAUTH_TOKEN is not set. Run `claude setup-token` and put "
            "the token in .env (LLM_AUTH_MODE=subscription)."
        )
    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError as exc:
        raise LLMConfigError(
            "claude-agent-sdk is not installed. `pip install -r requirements-dev.txt` "
            "(or `pip install claude-agent-sdk`) to use LLM_AUTH_MODE=subscription."
        ) from exc

    # The Agent SDK resolves credentials ANTHROPIC_API_KEY -> ANTHROPIC_AUTH_TOKEN ->
    # ... -> CLAUDE_CODE_OAUTH_TOKEN, so a stray API key silently shadows the token
    # and bills API credits. Force the subprocess to see only the subscription token.
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = settings.claude_code_oauth_token
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
    # Keep repo CLAUDE.md / auto-memory out of every completion (belt-and-suspenders
    # with ClaudeAgentOptions(setting_sources=[])).
    os.environ.setdefault("CLAUDE_CODE_DISABLE_AUTO_MEMORY", "1")

    return ClaudeSubscriptionChatModel(agent_model=model)


def _content_to_text(content: object) -> str:
    """Normalise a LangChain message content (str or block list) to plain text."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts).strip()
    return str(content).strip()


class ClaudeSubscriptionChatModel(BaseChatModel):
    """LangChain chat model backed by a Claude Pro/Max subscription (dev-only).

    Drives ``claude_agent_sdk.query`` (which authenticates via
    ``CLAUDE_CODE_OAUTH_TOKEN``) as a single-turn, tool-free completion and adapts
    the streamed messages back into a LangChain ``ChatResult``.
    """

    agent_model: str | None = None

    @property
    def _llm_type(self) -> str:
        return "claude-subscription"

    @staticmethod
    def _split(messages: list[BaseMessage]) -> tuple[str, str | None]:
        """Flatten LangChain messages into (prompt, system_prompt) for the SDK."""
        system_parts: list[str] = []
        turn_parts: list[str] = []
        for message in messages:
            text = _content_to_text(message.content)
            if not text:
                continue
            if isinstance(message, SystemMessage):
                system_parts.append(text)
            elif isinstance(message, AIMessage):
                turn_parts.append(f"Assistant: {text}")
            else:  # HumanMessage and anything else -> user turn
                turn_parts.append(text)
        system = "\n\n".join(system_parts) or None
        prompt = "\n\n".join(turn_parts)
        return prompt, system

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            ResultMessage,
            TextBlock,
            query,
        )

        prompt, system = self._split(messages)
        options = ClaudeAgentOptions(
            system_prompt=system,
            model=self.agent_model,
            max_turns=1,
            allowed_tools=[],
            setting_sources=[],
        )
        parts: list[str] = []
        final: str | None = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                parts.extend(
                    block.text for block in message.content if isinstance(block, TextBlock)
                )
            elif isinstance(message, ResultMessage):
                final = getattr(message, "result", None)
        text = final if final else "".join(parts)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        # The pipeline is async and uses .ainvoke() -> _agenerate; this sync bridge
        # exists only to satisfy BaseChatModel's abstract interface.
        import asyncio

        return asyncio.run(self._agenerate(messages, stop=stop))
