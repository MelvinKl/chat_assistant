from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent / ".env"


class LLMSetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_LLM_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field("ollama")
