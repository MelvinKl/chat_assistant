from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComponentSetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_COMPONENTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    apis: list[str] = Field(default=[])
