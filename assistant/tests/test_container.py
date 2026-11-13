"""
Unit-tests for the dependency container bindings.

Run with e.g.:

    $ pytest tests/test_container.py -vv

"""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import inject
import pytest
import yaml
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from assistant.impl.graph.chat_graph import ChatGraph
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import MCPSettings
from assistant.impl.stages.stage import Stage

REPO_ROOT = Path(__file__).resolve().parents[2]
HELM_VALUES = REPO_ROOT / "infrastructure" / "helm" / "values.yaml"

# Environment scaffolding mirroring tests/test_health_endpoints.py: dummy
# values for the settings the container consumes; the MCP and subagent config
# paths point at non-existent files, so the container binds empty server and
# subagent lists.
ENV = {
    "SETTINGS_OPENAI_API_KEY": "test-api-key",
    "SETTINGS_OPENAI_MODEL": "test-model",
    "SETTINGS_OPENAI_BASE_URL": "http://test-url",
    "SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT": "question system prompt",
    "SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT": "question user prompt",
    "SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT": "answer system prompt",
    "SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT": "answer user prompt",
    "SETTINGS_PROMPTS_PREPROCESSING_SYSTEM_PROMPT": "preprocessing system prompt",
    "SETTINGS_PROMPTS_POSTPROCESSING_SYSTEM_PROMPT": "postprocessing system prompt",
    "SETTINGS_ADDITIONAL_INFORMATION": "additional information",
    "MCP_SETTINGS_PATH": "/tmp/non_existent_mcp_config.json",  # noqa: S108
    "SUBAGENT_SETTINGS_PATH": "/tmp/non_existent_subagent_config.json",  # noqa: S108
}


@pytest.fixture
def configured_container():
    """Configure the container against the controlled environment above.

    Runs the container's ``configure()`` with the test environment in place,
    then restores the original environment and re-runs the configuration, so
    the injector holds the same bindings the test session started with.
    """
    old_env = os.environ.copy()
    for name in ENV:
        os.environ.pop(name, None)
    os.environ.update(ENV)
    from assistant.assistant_container import configure

    try:
        configure()
        injector = inject.get_injector_or_die()
        yield {
            "question_rephraser": injector.get_instance("question_rephraser"),
            "answer_rephraser": injector.get_instance("answer_rephraser"),
            "preprocessing": injector.get_instance("preprocessing"),
            "postprocessing": injector.get_instance("postprocessing"),
        }
    finally:
        os.environ.clear()
        os.environ.update(old_env)
        configure()


@pytest.fixture
def deep_agent_config(tmp_path):
    """Configure the container with an MCP server config and a subagents config.

    The MCP config carries one server without an agent assignment (whose
    tools go to the main agent) and one server with the agent ``weather``
    (whose tools go to the subagent ``weather``); the subagents config
    carries the subagents ``weather`` and ``ghost``, the latter matching no
    server agent. The mcp client connections and the deep agent creation
    are mocked, and the original environment and container configuration are
    restored afterwards, so the injector holds the same bindings the test
    session started with.
    """
    mcp_config = tmp_path / "mcp_settings.json"
    mcp_config.write_text(
        json.dumps(
            {
                "servers": [
                    {"name": "main-server", "command": "main-command", "transport": "stdio"},
                    {
                        "name": "weather-server",
                        "command": "weather-command",
                        "transport": "stdio",
                        "agent": "weather",
                    },
                ]
            }
        )
    )
    subagents_config = tmp_path / "subagents.json"
    subagents_config.write_text(
        json.dumps(
            {
                "subagents": [
                    {
                        "name": "weather",
                        "description": "the weather subagent description",
                        "system_prompt": "the weather subagent system prompt",
                    },
                    {
                        "name": "ghost",
                        "description": "the ghost subagent description",
                        "system_prompt": "the ghost subagent system prompt",
                    },
                ]
            }
        )
    )

    env = dict(ENV)
    env["MCP_SETTINGS_PATH"] = str(mcp_config)
    env["SUBAGENT_SETTINGS_PATH"] = str(subagents_config)
    old_env = os.environ.copy()
    for name in ENV:
        os.environ.pop(name, None)
    os.environ.update(env)
    main_tool = MagicMock()
    weather_tool = MagicMock()

    def client_side_effect(server_dict):
        client = MagicMock()
        name = next(iter(server_dict))
        client.get_tools = AsyncMock(return_value=[main_tool] if name == "main-server" else [weather_tool])
        return client

    from assistant.assistant_container import configure

    try:
        with (
            patch("assistant.assistant_container.MultiServerMCPClient", side_effect=client_side_effect),
            patch("assistant.assistant_container.create_deep_agent") as mock_create_deep_agent,
        ):
            configure()
            yield {
                "create_deep_agent": mock_create_deep_agent,
                "main_tool": main_tool,
                "weather_tool": weather_tool,
            }
    finally:
        os.environ.clear()
        os.environ.update(old_env)
        configure()


def chart_prompt_settings() -> dict:
    """Read the ``assistant.settings.prompt`` defaults of the helm chart."""
    values = yaml.safe_load(HELM_VALUES.read_text(encoding="utf-8"))
    return values["assistant"]["settings"]["prompt"]


def test_question_rephraser_uses_question_prompts(configured_container):
    """Implements "the question rephraser uses the question rephrasing prompts"
    (requirements/rephraser.feature)

    The question rephraser bound by the container carries the question
    rephrasing prompts of the prompt settings in its prompt template.
    """
    rephraser = configured_container["question_rephraser"]
    messages = rephraser._prompt_template.messages
    assert [type(message).__name__ for message in messages] == [
        "SystemMessagePromptTemplate",
        "HumanMessagePromptTemplate",
    ]
    assert messages[0].prompt.template == ENV["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"]
    assert messages[1].prompt.template == ENV["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"]


def test_answer_rephraser_uses_answer_prompts(configured_container):
    """Implements "the answer rephraser uses the answer rephrasing prompts"
    (requirements/rephraser.feature)

    The answer rephraser bound by the container carries the answer rephrasing
    prompts of the prompt settings in its prompt template.
    """
    rephraser = configured_container["answer_rephraser"]
    messages = rephraser._prompt_template.messages
    assert [type(message).__name__ for message in messages] == [
        "SystemMessagePromptTemplate",
        "HumanMessagePromptTemplate",
    ]
    assert messages[0].prompt.template == ENV["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"]
    assert messages[1].prompt.template == ENV["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"]


def test_default_question_prompts_cover_graph_state():
    """Implements "the default question rephrasing prompts cover the graph state"
    (requirements/rephraser.feature)

    The chart default question rephrasing prompts (the values the README's
    Prompts table documents) reference the question, history and additional
    information placeholders of the chat graph state, and the system prompt
    instructs rephrasing the question with the relevant information from the
    history.
    """
    prompts = chart_prompt_settings()
    user_prompt = prompts["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"]
    system_prompt = prompts["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"]
    for placeholder in ("{question}", "{history}", "{additional_info}"):
        assert placeholder in user_prompt
    assert "rephrase" in system_prompt
    assert "history" in system_prompt


def test_default_answer_prompts_rephrase_in_question_language():
    """Implements "the default answer rephrasing prompts rephrase in the question language"
    (requirements/rephraser.feature)

    The chart default answer rephrasing prompts rephrase in the question
    language: the system prompt references the ``{question_language}``
    placeholder and the user prompt references the question, the raw answer
    and the additional information.
    """
    prompts = chart_prompt_settings()
    system_prompt = prompts["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"]
    user_prompt = prompts["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"]
    assert "{question_language}" in system_prompt
    for placeholder in ("{question}", "{raw_answer}", "{additional_info}"):
        assert placeholder in user_prompt


def test_container_binds_agent_components(configured_container):
    """Implements "the container binds the agent components"
    (requirements/configuration.feature)

    Configuring the dependency container binds the agent components: the
    question rephraser is bound with the question rephrasing prompts, the
    answer rephraser is bound with the answer rephrasing prompts, the tools,
    the MCP settings, the information settings and the chat graph are bound,
    and the MCP agent is bound as the deep agent of the container's LLM.
    """
    injector = inject.get_injector_or_die()

    # The question rephraser is bound with the question rephrasing prompts.
    question_rephraser = configured_container["question_rephraser"]
    assert (
        question_rephraser._prompt_template.messages[0].prompt.template
        == ENV["SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT"]
    )
    assert (
        question_rephraser._prompt_template.messages[1].prompt.template
        == ENV["SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT"]
    )

    # The answer rephraser is bound with the answer rephrasing prompts.
    answer_rephraser = configured_container["answer_rephraser"]
    assert (
        answer_rephraser._prompt_template.messages[0].prompt.template
        == ENV["SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT"]
    )
    assert (
        answer_rephraser._prompt_template.messages[1].prompt.template
        == ENV["SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT"]
    )

    # The tools, the MCP settings, the information settings and the chat
    # graph are bound (the test environment configures no MCP servers).
    assert injector.get_instance("tools") == {}
    assert injector.get_instance(MCPSettings).servers == []
    assert injector.get_instance(InformationSettings).information == ENV["SETTINGS_ADDITIONAL_INFORMATION"]
    assert isinstance(injector.get_instance(ChatGraph), ChatGraph)

    # The MCP agent is bound as the deep agent of the container's LLM.
    llm = injector.get_instance(BaseChatModel)
    assert llm.model == ENV["SETTINGS_OPENAI_MODEL"]
    mcp_agent = injector.get_instance("mcp_agent")
    assert isinstance(mcp_agent, CompiledStateGraph)
    assert mcp_agent.config["metadata"]["ls_integration"] == "deepagents"
    # The deep agent's model node is built from the container's LLM.
    model_node = mcp_agent.nodes["model"]
    bound_closures = []
    for attribute in ("func", "afunc"):
        bound = getattr(model_node.bound, attribute, None)
        bound_closures.extend((cell.cell_contents for cell in bound.__closure__) if bound else [])
    assert llm in bound_closures


def test_container_binds_preprocessing_and_postprocessing_stages(configured_container):
    """Implements "the container binds the preprocessing and postprocessing stages"
    (requirements/configuration.feature)

    With configured LLM, tools, subagents, prompts and information
    settings, configuring the dependency container binds the
    preprocessing stage with the preprocessing system prompt and the
    postprocessing stage with the postprocessing system prompt.
    """
    # The preprocessing stage is bound with the preprocessing system prompt.
    preprocessing = configured_container["preprocessing"]
    assert isinstance(preprocessing, Stage)
    assert (
        preprocessing._prompt_template.messages[0].prompt.template
        == ENV["SETTINGS_PROMPTS_PREPROCESSING_SYSTEM_PROMPT"]
    )

    # The postprocessing stage is bound with the postprocessing system prompt.
    postprocessing = configured_container["postprocessing"]
    assert isinstance(postprocessing, Stage)
    assert (
        postprocessing._prompt_template.messages[0].prompt.template
        == ENV["SETTINGS_PROMPTS_POSTPROCESSING_SYSTEM_PROMPT"]
    )


def test_container_import_allows_nested_event_loops():
    """Implements "nested event loops are allowed for MCP tool loading"
    (requirements/configuration.feature)

    Importing the assistant container module applies nest-asyncio, so the
    asyncio event loop policy is patched to allow nested event loops — the
    container loads the MCP tools with asyncio.run on the already running
    loop of the MCP client, which only works on the patched policy.
    """
    import assistant.assistant_container  # noqa: F401

    assert asyncio._nest_patched is True
    assert asyncio.events.get_event_loop_policy().get_event_loop.__module__ == "nest_asyncio"

    # A second event loop may actually be run nested inside a running one.

    async def outer():
        async def inner():
            return 42

        return asyncio.run(inner())

    assert asyncio.run(outer()) == 42


def test_deep_agent_created_with_main_agent_tools_and_subagents(deep_agent_config):
    """Implements "the deep agent is created with the main agent tools and the subagents"
    (requirements/subagents.feature)

    When the dependency container is configured with the LLM, main agent
    tools and configured subagents, a deep agent is created with the LLM,
    the main agent receives the tools of the server without an agent
    assignment, and each configured subagent is passed to the deep agent.
    """
    call = deep_agent_config["create_deep_agent"].call_args
    assert call is not None

    # The deep agent is created with the LLM the container configured.
    llm = inject.get_injector_or_die().get_instance(BaseChatModel)
    assert call.kwargs["model"] is llm

    # The main agent receives the tools without an agent assignment.
    assert call.kwargs["tools"] == [deep_agent_config["main_tool"]]

    # Each configured subagent is passed to the deep agent.
    subagents = call.kwargs["subagents"]
    assert [subagent["name"] for subagent in subagents] == ["weather", "ghost"]
    for subagent in subagents:
        assert set(subagent) == {"name", "description", "system_prompt", "tools"}


def test_subagent_receives_tools_of_assigned_servers(deep_agent_config):
    """Implements "a subagent receives the tools of its assigned servers"
    (requirements/subagents.feature)

    Given a subagent named weather and an mcp server with the agent
    weather, when the tools of the servers are loaded, the subagent
    weather receives the tools of the server.
    """
    subagents = deep_agent_config["create_deep_agent"].call_args.kwargs["subagents"]
    weather = next(subagent for subagent in subagents if subagent["name"] == "weather")
    assert weather["tools"] == [deep_agent_config["weather_tool"]]


def test_subagent_without_assigned_servers_receives_no_tools(deep_agent_config):
    """Implements "a subagent without assigned servers receives no tools"
    (requirements/subagents.feature)

    Given a subagent whose name matches no mcp server agent, when the tools
    of the servers are loaded, the subagent receives an empty tool list.
    """
    subagents = deep_agent_config["create_deep_agent"].call_args.kwargs["subagents"]
    ghost = next(subagent for subagent in subagents if subagent["name"] == "ghost")
    assert ghost["tools"] == []
