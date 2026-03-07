from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InformationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_ADDITIONAL_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    information: str = Field(default="")
