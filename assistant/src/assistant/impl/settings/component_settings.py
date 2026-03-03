from pydantic import Field
from pydantic_settings import BaseSettings


class ComponentSetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_COMPONENTS_"

    apis: list[str] = Field()
