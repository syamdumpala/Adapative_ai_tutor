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

    # Claude / LangChain
    anthropic_api_key: str | None = None
    llm_model: str = "claude-opus-4-8"


settings = Settings()
