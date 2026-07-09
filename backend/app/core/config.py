from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # PostgreSQL — async driver (asyncpg). Override via DATABASE_URL in .env.
    database_url: str = "postgresql+asyncpg://localhost:5432/adaptive_tutor"

    # JWT auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # LLM provider selection (see app/core/llm.py). All env-driven, so switching
    # dev <-> prod is a config change, never a code change.
    llm_provider: str = "anthropic"  # anthropic | openai | google | local
    llm_auth_mode: str = "subscription"  # subscription | api_key (Anthropic only)
    llm_model: str = "claude-opus-4-8"  # any model the chosen provider supports

    # Provider credentials — set only the one(s) you use.
    claude_code_oauth_token: str | None = None  # dev: Claude subscription (claude setup-token)
    anthropic_api_key: str | None = None  # prod: Anthropic API key
    openai_api_key: str | None = None  # prod: OpenAI API key
    google_api_key: str | None = None  # prod: Google Gemini API key

    # Local LLM server (LM Studio / Ollama / vLLM / llama.cpp — OpenAI-compatible).
    # Set LLM_PROVIDER=local and point LOCAL_BASE_URL at the server's /v1 endpoint.
    local_base_url: str | None = None  # e.g. http://localhost:1234/v1 (LM Studio)
    local_api_key: str | None = None  # most local servers ignore this; any placeholder works

    # Observability — LangSmith tracing (per-agent inputs/outputs/models).
    # Tri-state: a present LANGSMITH_API_KEY auto-enables tracing. Set
    # LANGSMITH_TRACING=false to force it off, or =true to require it.
    langsmith_tracing: bool | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str = "adaptive-ai-tutor"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    # Debug: print each agent's prompt input + output per request, and include the
    # {agent: {input, output}} dict in the /tutor/ask response. Dev-only (verbose,
    # exposes prompts) — keep false in production.
    debug_agent_io: bool = False

    # CORS — comma-separated origins allowed to call the API from a browser.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# The insecure default JWT secret; used to warn if it isn't overridden.
DEFAULT_JWT_SECRET = "change-me-in-production"

settings = Settings()
