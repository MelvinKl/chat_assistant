import asyncio

import inject
import nest_asyncio
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from assistant.impl.graph.chat_graph import ChatGraph
from assistant.impl.rephraser.rephraser import Rephraser
from assistant.impl.settings.mcp_server_settings import (
    MCPSettings,
    load_mcp_settings_from_json,
)
from assistant.impl.settings.openai_settings import OpenAISetttings
from assistant.impl.settings.prompt_settings import PromptSettings

# Apply the patch to allow nested event loops
nest_asyncio.apply()


def _di_config(binder: Binder):
    settings_openai = OpenAISetttings()
    settings_prompt = PromptSettings()
    settings_mcp = load_mcp_settings_from_json()

    llm = ChatOpenAI(
        model=settings_openai.model,
        base_url=settings_openai.base_url,
        api_key=settings_openai.api_key,
    )
    server_dict = {}
    for server_definition in settings_mcp.servers:
        if server_definition.transport == "stdio":
            server_dict[server_definition.name] = {
                "command": server_definition.command,
                "args": server_definition.args,
                "transport": "stdio",
            }
        else:
            server_dict[server_definition.name] = {
                "url": server_definition.url,
                "transport": server_definition.transport,                
            }
            if server_definition.headers:
                server_dict[server_definition.name]["headers"] = server_definition.headers
                
    mcp_client = MultiServerMCPClient(server_dict)
    tools = asyncio.run(mcp_client.get_tools())
    mcp_agent = create_react_agent(llm, tools)

    binder.bind(
        "question_rephraser",
        Rephraser(
            llm=llm,
            system_prompt=settings_prompt.rephrase_question_system_prompt,
            user_prompt=settings_prompt.rephrase_question_user_prompt,
        ),
    )
    binder.bind(
        "answer_rephraser",
        Rephraser(
            llm=llm,
            system_prompt=settings_prompt.rephrase_answer_system_prompt,
            user_prompt=settings_prompt.rephrase_answer_user_prompt,
        ),
    )
    binder.bind(BaseChatModel, llm)
    binder.bind(MCPSettings, load_mcp_settings_from_json())
    binder.bind_to_constructor(ChatGraph, ChatGraph)
    binder.bind("mcp_agent", mcp_agent)


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
