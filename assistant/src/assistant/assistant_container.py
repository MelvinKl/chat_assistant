# coding: utf-8
import asyncio
import logging
from typing import Optional

import inject
import nest_asyncio
from deepagents import create_deep_agent
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from assistant.impl.graph.chat_graph import ChatGraph
from assistant.impl.mcp_sampling import create_sampling_callback
from assistant.impl.rephraser.rephraser import Rephraser
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import (
    MCPSettings,
    load_mcp_settings_from_json,
)
from assistant.impl.settings.openai_settings import OpenAISetttings
from assistant.impl.settings.prompt_settings import PromptSettings
from assistant.impl.settings.subagent_settings import (
    load_subagent_settings_from_json,
)
from assistant.impl.settings.system_one_settings import SystemOneSettings
from assistant.impl.stages.stage import Stage

# Apply the patch to allow nested event loops
nest_asyncio.apply()

logger = logging.getLogger(__name__)


def _get_mcp_tools(
    settings_mcp: MCPSettings,
    llm: BaseChatModel,
    server_tools: Optional[dict[str, list[BaseTool]]] = None,
) -> dict[str | None, BaseTool]:
    """Load the tools of every configured MCP server.

    Returns the tools grouped under each server's ``agent`` key — ``None`` the
    main agent, a subagent name that subagent, ``preprocessing``/
    ``postprocessing`` the respective stage. When ``server_tools`` is given,
    the loaded tools of every server that loaded successfully are additionally
    recorded in it, keyed by the server name.
    """
    tools: dict[str | None, list[BaseTool]] = {}
    sampling_callback = create_sampling_callback(llm)

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
        # The installed langchain-mcp-adapters takes no callback at the client
        # level: the callback rides the connection dict's session_kwargs, which
        # the adapter's session creators forward to the mcp SDK ClientSession.
        server_dict[server_definition.name]["session_kwargs"] = {"sampling_callback": sampling_callback}
        mcp_client = MultiServerMCPClient(server_dict)
        try:
            logger.info("Adding mcp-server %s" % server_definition.name)
            loaded_tools = asyncio.run(mcp_client.get_tools())
            if server_definition.agent not in tools:
                tools[server_definition.agent] = []
            tools[server_definition.agent] += loaded_tools
            if server_tools is not None:
                server_tools[server_definition.name] = loaded_tools
        except Exception as e:
            logger.error("Could not load MCP Tools from server %s\t%s " % (server_definition.name, e))
    return tools


def _di_config(binder: Binder) -> None:
    settings_openai = OpenAISetttings()
    settings_information = InformationSettings()
    settings_prompt = PromptSettings()
    settings_mcp = load_mcp_settings_from_json()
    settings_subagents = load_subagent_settings_from_json()
    settings_system_one = SystemOneSettings()

    llm = ChatOpenAI(
        model=settings_openai.model,
        base_url=settings_openai.base_url,
        api_key=settings_openai.api_key,
    )

    server_tools: dict[str, list[BaseTool]] = {}
    tools = _get_mcp_tools(settings_mcp, llm, server_tools)

    def stage_mcp_servers(stage: str) -> dict[str, list[BaseTool]]:
        """The MCP servers assigned to one question answering stage.

        Keyed by the server name: the loaded tools of each server whose
        ``agent`` field names the stage and that loaded successfully.
        """
        return {
            server.name: server_tools[server.name]
            for server in settings_mcp.servers
            if server.agent == stage and server.name in server_tools
        }

    subagents = [
        {
            "name": subagent.name,
            "description": subagent.description,
            "system_prompt": subagent.system_prompt,
            "tools": tools.get(subagent.name, []),
        }
        for subagent in settings_subagents.subagents
    ]

    mcp_agent = create_deep_agent(
        model=llm,
        tools=tools.get(None, []),
        subagents=subagents,
    )

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
    binder.bind(
        "preprocessing",
        Stage(
            llm=llm,
            system_prompt=settings_prompt.preprocessing_system_prompt,
            user_prompt="The question is: {question}",
            tools=tools.get("preprocessing", []),
            mcp_servers=stage_mcp_servers("preprocessing"),
            system_one=settings_system_one,
        ),
    )
    binder.bind(
        "postprocessing",
        Stage(
            llm=llm,
            system_prompt=settings_prompt.postprocessing_system_prompt,
            user_prompt="The returned answer is: {processed_answer}",
            tools=tools.get("postprocessing", []),
            mcp_servers=stage_mcp_servers("postprocessing"),
            system_one=settings_system_one,
        ),
    )
    binder.bind("tools", tools)
    binder.bind(BaseChatModel, llm)
    binder.bind(MCPSettings, load_mcp_settings_from_json())
    binder.bind(InformationSettings, settings_information)
    # The chat graph receives the SystemOne model (the configured SystemOne
    # settings) and the MCP settings: on invocation with a user question the
    # SystemOne model determines whether the goal can be reached at all with
    # the available MCP servers.
    binder.bind_to_constructor(
        ChatGraph,
        lambda: ChatGraph(system_one=settings_system_one, mcp_settings=settings_mcp),
    )
    binder.bind("mcp_agent", mcp_agent)


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
