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

    api_key: str = Field()
    embedder: str = Field()
    model: str = Field()
    base_url: str = Field()
