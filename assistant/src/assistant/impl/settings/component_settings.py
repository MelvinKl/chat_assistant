from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class ComponentSetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_COMPONENTS_"
        env_ignore_empty = True

    apis: list[str] = Field(default_factory=list)

    @field_validator("apis", mode="before")
    @classmethod
    def parse_apis(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            if "[" in v:
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v
