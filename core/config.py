from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    notion_api_key: str | None = None
    notion_page_id: str | None = None
    mcp_server_url: str = "https://api.notion.com/v1"
    webhook_secret: str = "dev-secret"
    database_url: str = "sqlite:///./living-docs.db"
    repo: str = "your-org/your-repo"
    confidence_threshold: int = 80

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
