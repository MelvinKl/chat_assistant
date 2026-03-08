from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent / ".env"


class OpenAISetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_OPENAI_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = Field(default="dummy-key")
    embedder: str = Field(default="text-embedding-3-small")
    model: str = Field(default="gpt-4o-mini")
    base_url: str = Field(default="https://api.openai.com/v1")
