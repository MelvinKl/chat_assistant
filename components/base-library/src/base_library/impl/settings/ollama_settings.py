from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_OLLAMA_"

    model: str = Field(default="llama3.2:3b")
    url: str = Field(default="http://open-webui-ollama:11434")
