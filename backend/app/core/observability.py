"""LangSmith observability wiring.

LangChain / LangGraph read ``LANGSMITH_*`` environment variables at run time. We set
them from application settings at startup so every graph run, agent node, and LLM
call is traced (inputs, outputs, model, latency, tokens) — visible per session and
per agent in the LangSmith UI.

Tracing is **opt-in**: it only turns on when ``LANGSMITH_TRACING=true`` and a
``LANGSMITH_API_KEY`` are set. When off, this is a no-op (no runtime overhead).
"""

import logging
import os

from app.core.config import settings

logger = logging.getLogger("app")


def configure_observability() -> bool:
    """Enable LangSmith tracing if configured. Returns True when tracing is on.

    A present ``LANGSMITH_API_KEY`` turns tracing on automatically. Set
    ``LANGSMITH_TRACING=false`` to force it off even when a key is present, or
    ``=true`` to require a key (warns if missing).
    """
    explicit = settings.langsmith_tracing  # True | False | None (auto)
    key = settings.langsmith_api_key

    if explicit is False:
        logger.info("LangSmith tracing disabled (LANGSMITH_TRACING=false).")
        return False
    if not key:
        if explicit is True:
            logger.warning("LANGSMITH_TRACING=true but LANGSMITH_API_KEY is not set — tracing off.")
        else:
            logger.info("LangSmith tracing off (set LANGSMITH_API_KEY to enable).")
        return False

    # New (LANGSMITH_*) and legacy (LANGCHAIN_*) names, for broad SDK compatibility.
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint

    logger.info(
        "LangSmith tracing enabled (project=%s, endpoint=%s).",
        settings.langsmith_project,
        settings.langsmith_endpoint,
    )
    return True
