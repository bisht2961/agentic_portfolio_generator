from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # OpenRouter API Setup
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Optional headers for OpenRouter rankings / identification
    app_name: str = "Agentic Portfolio Generator"
    site_url: str = "http://localhost:3000"

    # Per-Agent Configurable Models
    ingestion_model: str = "google/gemini-2.0-flash-001"
    storyteller_model: str = "anthropic/claude-3.5-sonnet"
    design_model: str = "openai/gpt-4o-mini"
    reviewer_model: str = "meta-llama/llama-3.3-70b-instruct"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """Cached singleton instance of settings."""
    return Settings()

settings = get_settings()