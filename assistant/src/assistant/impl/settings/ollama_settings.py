from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_OLLAMA_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    model: str = Field(default="llama3.2:3b")
    url: str = Field(default="http://open-webui-ollama:11434")
