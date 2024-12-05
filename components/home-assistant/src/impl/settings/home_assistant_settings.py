from pydantic import Field
from pydantic_settings import BaseSettings


class HomeAssistantSetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_HOMEASSISTANT_"

    apikey: str = Field()
    url: str = Field()
