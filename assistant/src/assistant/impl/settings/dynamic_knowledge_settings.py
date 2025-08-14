from pydantic import Field
from pydantic_settings import BaseSettings


class DynamicKnowledgeSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_DYNAMIC_KNOWLEDGE_"

    enabled: bool = Field()
    collection_name: str = Field()
    db_host: str = Field()
    max_items: int = Field(default=25)
    score_threshold: float = Field(default=0.25)
    system_prompt: str = Field()
    user_prompt: str = Field()
