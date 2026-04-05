import json
import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Subagent(BaseModel):
    name: str
    description: str
    system_prompt: str    


class SubagentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_SUBAGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    subagents: list[Subagent] = Field()


def load_subagent_settings_from_json(
    json_file_path="/config/subagents/SETTINGS_SUBAGENTS",
) -> SubagentSettings:
    # Check for environment variable override
    path = os.environ.get("SUBAGENT_SETTINGS_PATH", json_file_path)

    try:
        with open(path, "r") as f:
            data = json.load(f)

        cleaned_data = {"subagents": data["subagents"]} if "subagents" in data else {}
        return SubagentSettings(**cleaned_data)
    except FileNotFoundError:
        return SubagentSettings(subagents=[])
    except json.JSONDecodeError as e:
        raise ValueError("MCP settings file contains invalid JSON") from e
