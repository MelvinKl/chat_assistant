from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field("ollama")
