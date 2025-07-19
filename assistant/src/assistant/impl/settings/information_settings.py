from pydantic import Field
from pydantic_settings import BaseSettings


class InformationSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_ADDITIONAL_"

    information: str = Field()
