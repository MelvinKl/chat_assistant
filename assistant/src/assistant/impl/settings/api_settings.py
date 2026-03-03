from pydantic import Field
from pydantic_settings import BaseSettings


class APISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_API_"

    name: str = Field(default="api_name")
    description: str = Field(default="api_description")
