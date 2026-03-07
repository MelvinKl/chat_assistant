from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent / ".env"


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_OLLAMA_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = Field(default="llama3.2:3b")
    url: str = Field(default="http://open-webui-ollama:11434")
