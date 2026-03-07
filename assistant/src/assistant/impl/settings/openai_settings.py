from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_OPENAI_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_key: str = Field(default="sk-...")
    embedder: str = Field(default="text-embedding-3-small")
    model: str = Field(default="gpt-4o")
    base_url: str = Field(default="https://api.openai.com/v1")
