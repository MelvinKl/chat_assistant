from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_API_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    name: str = Field(default="")
    description: str = Field(default="")
