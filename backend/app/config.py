from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLD Practice Platform API"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./lld_platform.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    # Optional LLM evaluation configuration
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def has_llm_configured(self) -> bool:
        return bool(self.llm_api_key and self.llm_api_key.strip())


settings = Settings()
