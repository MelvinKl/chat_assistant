from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_OPENAI_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_key: str = Field(default="")
    embedder: str = Field(default="")
    model: str = Field(default="")
    base_url: str = Field(default="")
