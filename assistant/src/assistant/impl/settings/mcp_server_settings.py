import json
import os

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MCPServer(BaseModel):
    url: str = ""
    name: str
    command: str = ""
    args: list[str] = []
    env: str = ""
    transport: str
    headers: dict[str, str] | None = None


class MCPSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_MCP_"

    servers: list[MCPServer] = Field()


def load_mcp_settings_from_json() -> MCPSettings:
    json_file_path = os.getenv("SETTINGS_MCP_SERVERS_PATH", "/config/mcp/SETTINGS_MCP_SERVERS")
    if not os.path.exists(json_file_path):
        return MCPSettings(servers=[])

    with open(json_file_path, "r") as f:
        data = json.load(f)

    cleaned_data = {"servers": data["servers"]} if "servers" in data else {}
    return MCPSettings(**cleaned_data)
