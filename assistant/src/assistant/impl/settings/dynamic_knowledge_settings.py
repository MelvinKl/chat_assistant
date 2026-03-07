from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamicKnowledgeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_DYNAMIC_KNOWLEDGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=False)
    collection_name: str = Field(default="test_collection")
    db_host: str = Field(default="localhost")
    max_items: int = Field(default=25)
    score_threshold: float = Field(default=0.25)
    system_prompt: str = Field(default="")
    user_prompt: str = Field(default="")
