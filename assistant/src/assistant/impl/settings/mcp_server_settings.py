import json

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


import os

def load_mcp_settings_from_json(json_file_path=None) -> MCPSettings:
    if json_file_path is None:
        json_file_path = os.getenv("SETTINGS_MCP_PATH", "/config/mcp/SETTINGS_MCP_SERVERS")
    
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
        cleaned_data = {"servers": data["servers"]} if "servers" in data else {}
    except FileNotFoundError:
        cleaned_data = {"servers": []}
        
    return MCPSettings(**cleaned_data)
