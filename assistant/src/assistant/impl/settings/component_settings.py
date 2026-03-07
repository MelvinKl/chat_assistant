from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent / ".env"


class ComponentSetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_COMPONENTS_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    apis: list[str] = Field(default_factory=list)
