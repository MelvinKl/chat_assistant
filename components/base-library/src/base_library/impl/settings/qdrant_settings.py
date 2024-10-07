from pydantic import Field
from pydantic_settings import BaseSettings


class QdrantSetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_QDRANT_"

    collection_name: str = Field(default="collection")
    url: str = Field(default="http://assistant-qdrant:6333")
