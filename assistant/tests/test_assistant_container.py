"""Unit tests for assistant_container.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import inject

from assistant.assistant_container import _di_config
from assistant.impl.settings.mcp_server_settings import MCPServer, MCPSettings
from assistant.impl.settings.prompt_settings import PromptSettings
from assistant.impl.settings.subagent_settings import SubagentSettings
from assistant.impl.stages.stage import Stage


class TestDiConfig:
    def test_binds_stage_runnables(self):
        """_di_config binds the preprocess and postprocess stages with their own prompts and tools."""
        fake_llm = MagicMock(name="llm")
        fake_tool = MagicMock(name="mcp_tool")

        with (
            patch("assistant.assistant_container.ChatOpenAI", return_value=fake_llm),
            patch("assistant.assistant_container.create_deep_agent", return_value=MagicMock(name="mcp_agent")),
            patch("assistant.assistant_container.MultiServerMCPClient") as mock_mcp_client_cls,
            patch(
                "assistant.assistant_container.load_mcp_settings_from_json",
                return_value=MCPSettings(
                    servers=[MCPServer(name="staged", command="cmd", transport="stdio", stage="preprocess")]
                ),
            ),
            patch(
                "assistant.assistant_container.load_subagent_settings_from_json",
                return_value=SubagentSettings(subagents=[]),
            ),
            patch(
                "assistant.assistant_container.PromptSettings",
                return_value=PromptSettings(
                    preprocess_system_prompt="PRE_SYSTEM",
                    preprocess_user_prompt="PRE_USER",
                    postprocess_system_prompt="POST_SYSTEM",
                    postprocess_user_prompt="POST_USER",
                ),
            ),
        ):
            mock_client = MagicMock(name="mcp_client")
            mock_client.get_tools = AsyncMock(return_value=[fake_tool])
            mock_mcp_client_cls.return_value = mock_client

            inject.configure(_di_config, allow_override=True, clear=True)
            injector = inject.get_injector_or_die()

            preprocess_stage = injector.get_instance("preprocess_stage")
            postprocess_stage = injector.get_instance("postprocess_stage")

            # Both stages are bound as Stage runnables ...
            assert isinstance(preprocess_stage, Stage)
            assert isinstance(postprocess_stage, Stage)
            # ... each with its own system and user prompt ...
            pre_messages = preprocess_stage._prompt_template.format_messages()
            post_messages = postprocess_stage._prompt_template.format_messages()
            assert [(type(m).__name__, m.content) for m in pre_messages] == [
                ("SystemMessage", "PRE_SYSTEM"),
                ("HumanMessage", "PRE_USER"),
            ]
            assert [(type(m).__name__, m.content) for m in post_messages] == [
                ("SystemMessage", "POST_SYSTEM"),
                ("HumanMessage", "POST_USER"),
            ]
            # ... using the configured llm (the tool-capable stage gets the tool-bound llm) ...
            assert preprocess_stage._llm is fake_llm.bind_tools.return_value
            assert postprocess_stage._llm is fake_llm
            # ... and the mcp tools of the servers that are assigned to that stage.
            assert preprocess_stage._tools == {fake_tool.name: fake_tool}
            assert postprocess_stage._tools == {}
            # Servers that are assigned to a stage must not be handed to the main agent.
            assert set(injector.get_instance("tools")) == {"preprocess"}

        # Restore the regular (unpatched) configuration of the global injector.
        inject.configure(_di_config, allow_override=True, clear=True)
