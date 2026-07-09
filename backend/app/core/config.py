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


settings = Settings()
