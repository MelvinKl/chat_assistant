import asyncio
import logging

import inject
import nest_asyncio
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.prebuilt import create_react_agent
from qdrant_client import QdrantClient

from assistant.impl.dynamic_knowledge.dummy_knowledge_db import DummyKnowledgeDB
from assistant.impl.dynamic_knowledge.qdrant_knowledge_db import QdrantKnowledgeDB
from assistant.impl.graph.chat_graph import ChatGraph
from assistant.impl.rephraser.rephraser import Rephraser
from assistant.impl.settings.dynamic_knowledge_settings import DynamicKnowledgeSettings
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import (
    MCPSettings,
    load_mcp_settings_from_json,
)
from assistant.impl.settings.openai_settings import OpenAISetttings
from assistant.impl.settings.prompt_settings import PromptSettings
from assistant.interfaces.knowledge_db import KnowledgeDB

# Apply the patch to allow nested event loops
nest_asyncio.apply()

logger = logging.getLogger(__name__)


def _get_mcp_tools(settings_mcp: MCPSettings) -> list[BaseTool]:
    tools = []

    for server_definition in settings_mcp.servers:
        server_dict = {}
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
        try:
            server_tools = asyncio.run(mcp_client.get_tools())
            tools += server_tools
        except Exception as e:
            logger.error("Could not load MCP Tools from server %s\t%s " % (server_definition.name, e))
    return tools


def _init_dynamic_knowledge(binder: Binder, settings_openai: OpenAISetttings) -> None:
    settings_dynamic_knowledge = DynamicKnowledgeSettings()

    binder.bind("dynamic_knowledge_enabled", settings_dynamic_knowledge.enabled)

    if not settings_dynamic_knowledge.enabled:
        binder.bind_to_constructor(KnowledgeDB, DummyKnowledgeDB)
        return

    binder.bind(
        "dynamic_knowledge_prompt_template",
        ChatPromptTemplate.from_messages(
            [("system", settings_dynamic_knowledge.system_prompt), ("user", settings_dynamic_knowledge.user_prompt)]
        ),
    )
    embedder = OpenAIEmbeddings(
        model=settings_openai.embedder,
        openai_api_base=settings_openai.base_url,
        openai_api_key=settings_openai.api_key,
    )
    binder.bind(OpenAIEmbeddings, embedder)
    binder.bind_to_constructor(KnowledgeDB, QdrantKnowledgeDB)
    binder.bind(
        QdrantClient,
        QdrantClient(location=settings_dynamic_knowledge.db_host)
    )


def _di_config(binder: Binder) -> None:
    settings_openai = OpenAISetttings()
    settings_prompt = PromptSettings()
    settings_information = InformationSettings()

    settings_mcp = load_mcp_settings_from_json()
    _init_dynamic_knowledge(binder, settings_openai)

    llm = ChatOpenAI(
        model=settings_openai.model,
        base_url=settings_openai.base_url,
        api_key=settings_openai.api_key,
    )
    tools = _get_mcp_tools(settings_mcp)
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
    binder.bind(InformationSettings, settings_information)
    binder.bind_to_constructor(ChatGraph, ChatGraph)
    binder.bind("mcp_agent", mcp_agent)


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
