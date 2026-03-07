from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComponentSetttings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_COMPONENTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    apis: list[str] = Field(default_factory=list)

    @field_validator("apis", mode="before")
    @classmethod
    def parse_apis(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            if "[" in v:
                import json
                import contextlib

                with contextlib.suppress(Exception):
                    return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v
