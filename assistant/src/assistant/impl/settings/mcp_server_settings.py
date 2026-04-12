import json
import os
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServer(BaseModel):
    name: str
    description: str = Field(default="")
    url: str
    transport: Literal["sse", "stdio"] = Field(default="sse")
    command: str | None = Field(default=None)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    servers: list[MCPServer] = Field(default_factory=list)
    strict: bool = Field(default=False)


def load_mcp_settings_from_json(
    json_file_path="/config/mcp/SETTINGS_MCP",
) -> MCPSettings:
    # Check for environment variable override
    path = os.environ.get("MCP_SETTINGS_PATH", json_file_path)

    try:
        with open(path, "r") as f:
            data = json.load(f)

        cleaned_data = {"servers": data["servers"]} if "servers" in data else {}
        # Handle strict field if present in JSON
        if "strict" in data:
            cleaned_data["strict"] = data["strict"]
        return MCPSettings(**cleaned_data)
    except FileNotFoundError:
        return MCPSettings(servers=[], strict=False)
    except json.JSONDecodeError as e:
        raise ValueError("MCP settings file contains invalid JSON") from e
