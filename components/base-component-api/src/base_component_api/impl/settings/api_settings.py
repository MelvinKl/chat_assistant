from pydantic import Field
from pydantic_settings import BaseSettings


class APISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_API_"

    name: str = Field()
    description: str = Field()
