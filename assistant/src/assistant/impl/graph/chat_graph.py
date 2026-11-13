"""Module for the string enum class GraphNodeNames and the DefaultChatGraph class."""

import logging
from enum import StrEnum
from pathlib import Path
from typing import Any, Optional

import inject
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.base import RunnableSequence
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_openai import ChatOpenAI
from langdetect import detect
from langgraph.graph import END, START, StateGraph

from assistant.impl.graph.graph_state import GraphState
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import MCPSettings
from assistant.impl.settings.system_one_settings import SystemOneSettings

logger = logging.getLogger(__name__)

# The answer an unreachable goal is answered with: the invocation skips the
# stages up to the answer generation and informs the user that no MCP servers
# are currently available to help.
NO_MCP_SERVERS_ANSWER = "No MCP servers are currently available to help."


class GraphNodeNames(StrEnum):
    """Enum for names of the nodes in the ChatGraph"""

    PREPROCESSING = "preprocessing"
    REPHRASE_QUESTION = "rephrase_question"
    DETERMINE_LANGUAGE = "determine_language"
    DECIDE = "decide"
    REPHRASE_ANSWER = "rephrase_answer"
    POSTPROCESSING = "postprocessing"


class ChatGraph:
    """Langchain graph for executing requests against the chat assistant."""

    @inject.params(
        llm=BaseChatModel,
        question_rephraser="question_rephraser",
        answer_rephraser="answer_rephraser",
        mcp_agent="mcp_agent",
        preprocessing="preprocessing",
        postprocessing="postprocessing",
        information_settings=InformationSettings,
    )
    def __init__(
        self,
        llm: BaseChatModel,
        question_rephraser: Runnable,
        answer_rephraser: Runnable,
        mcp_agent: RunnableSequence,
        preprocessing: Runnable,
        postprocessing: Runnable,
        information_settings: InformationSettings,
        system_one: Optional[SystemOneSettings] = None,
        mcp_settings: Optional[MCPSettings] = None,
    ):
        self._information_settings = information_settings
        self._question_rephraser = question_rephraser
        self._answer_rephraser = answer_rephraser
        self._llm = llm
        self._mcp_agent = mcp_agent
        self._preprocessing = preprocessing
        self._postprocessing = postprocessing
        self._system_one = system_one if system_one is not None and system_one.model else None
        self._mcp_settings = mcp_settings
        self._state_graph = StateGraph(GraphState)
        self._graph = self._setup_graph()

    async def ainvoke(
        self,
        graph_input: list[tuple[str, str]],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        """
        Processes a chat assistant request and handles mcp calls.

        A graph built with a configured SystemOne model runs the
        goal-reachability determination before any node executes: when the
        SystemOne model concludes that the user's goal cannot be reached at
        all with the available MCP servers, the invocation skips the stages
        up to the answer generation and returns `NO_MCP_SERVERS_ANSWER`
        without running the graph.

        Parameters
        ----------
        graph_input : list[tuple[str, str]]
            The initial state used to initialize the GraphState.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The generated answer.
        """
        if not graph_input:
            return "No question has been found."

        try:
            question = graph_input[-1][1]
        except Exception as e:
            logger.error(e)
            return "No question has been found."
        if self._system_one is not None and not await self._determine_goal_reachable(question, config):
            logger.info(
                'The goal of question "%s" is unreachable with the available MCP servers',
                question,
            )
            return NO_MCP_SERVERS_ANSWER
        history = [f"{message[0]}: {message[1]}" for message in graph_input[0:-1]]

        state = GraphState.create(
            history=history,
            question=question,
            additional_info=self._information_settings.information,
        )

        logger.info("RECEIVED question: %s", state["question"])

        response_state = await self._graph.ainvoke(input=state, config=config)

        logger.info("GENERATED answer: %s", response_state["processed_answer"])

        return response_state["processed_answer"]

    async def _determine_goal_reachable(
        self,
        question: str,
        config: Optional[RunnableConfig] = None,
    ) -> bool:
        """Determine if the user's goal can be reached at all with the available MCP servers.

        The SystemOne model is created from the configured SystemOne settings
        and consulted with the question and the names of the MCP servers the
        assistant has available. A determination the model's answer does not
        express as unreachable keeps the invocation running.

        Parameters
        ----------
        question : str
            The question of the user the determination runs for.
        config : RunnableConfig
            configuration for the llm. Defaults to None

        Returns
        -------
        bool
            True when the model's answer does not state that the goal is
            unreachable with the available MCP servers
        """
        llm = ChatOpenAI(
            model=self._system_one.model,
            base_url=self._system_one.base_url,
            api_key=self._system_one.api_key,
        )
        server_names = [server.name for server in self._mcp_settings.servers] if self._mcp_settings else []
        servers = "none" if not server_names else ", ".join(server_names)
        prompt = (
            "You are the SystemOne model of a chat assistant. You determine whether a user's goal can be "
            f"reached at all with the MCP servers the assistant has available.\n"
            f"The user's question: {question}\n"
            f"The available MCP servers: {servers}\n"
            'Answer with exactly "reachable" or "unreachable".'
        )
        response = await llm.ainvoke(prompt, config)
        return "unreachable" not in response.content.lower()

    def draw_graph(self, relative_dir_path: Optional[str] = None) -> None:
        """
        Draw the graph and save it as a PNG file.

        Parameters
        ----------
        relative_dir_path : Optional[str]
            The relative directory path where the PNG file will be saved.
            If not provided, the current working directory will be used.
            (default None)

        Returns
        -------
        None
        """
        if relative_dir_path:
            p = Path.cwd() / relative_dir_path
        else:
            p = Path.cwd()
        p.mkdir(parents=True, exist_ok=True)
        img_name = p / "chat_graph.png"
        self._graph.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API, output_file_path=str(img_name.absolute())
        )

    #########
    # nodes #
    #########
    async def _preprocessing_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        preprocessed_question = await self._preprocessing.ainvoke(state, config)
        logger.info(
            'Preprocessed question "%s" to "%s"',
            state["question"],
            preprocessed_question,
        )
        return {"question": preprocessed_question}

    async def _determine_language_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question_language = detect(state["question"])
        logger.info(
            'Detected langauge for question "%s": %s',
            state["question"],
            question_language,
        )
        return {"question_language": question_language}

    async def _rephrase_question_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:

        rephrased_question = await self._question_rephraser.ainvoke(state, config)
        logger.info(
            'Rephrased question "%s" with history "%s" to %s',
            state["question"],
            state["history"],
            rephrased_question,
        )
        return {"question": rephrased_question}

    async def _answer_rephraser_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        rephrased_answer = await self._answer_rephraser.ainvoke(state, config)
        return {"processed_answer": rephrased_answer}

    async def _decide_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        answer = await self._mcp_agent.ainvoke({"messages": state["question"]}, config)
        answer = answer["messages"][-1].content
        return {"raw_answer": answer}

    async def _postprocessing_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        postprocessed_answer = await self._postprocessing.ainvoke(state, config)
        logger.info(
            'Postprocessed answer "%s" to "%s"',
            state["processed_answer"],
            postprocessed_answer,
        )
        return {"processed_answer": postprocessed_answer}

    def _add_nodes(self):
        self._state_graph.add_node(GraphNodeNames.PREPROCESSING, self._preprocessing_node)
        self._state_graph.add_node(GraphNodeNames.REPHRASE_QUESTION, self._rephrase_question_node)
        self._state_graph.add_node(GraphNodeNames.DETERMINE_LANGUAGE, self._determine_language_node)
        self._state_graph.add_node(GraphNodeNames.DECIDE, self._decide_node)
        self._state_graph.add_node(GraphNodeNames.REPHRASE_ANSWER, self._answer_rephraser_node)
        self._state_graph.add_node(GraphNodeNames.POSTPROCESSING, self._postprocessing_node)

    def _wire_graph(self):
        self._state_graph.add_edge(START, GraphNodeNames.PREPROCESSING)
        self._state_graph.add_edge(GraphNodeNames.PREPROCESSING, GraphNodeNames.DETERMINE_LANGUAGE)
        self._state_graph.add_edge(GraphNodeNames.PREPROCESSING, GraphNodeNames.REPHRASE_QUESTION)
        self._state_graph.add_edge(GraphNodeNames.REPHRASE_QUESTION, GraphNodeNames.DECIDE)
        self._state_graph.add_edge(
            [GraphNodeNames.DETERMINE_LANGUAGE, GraphNodeNames.DECIDE],
            GraphNodeNames.REPHRASE_ANSWER,
        )
        self._state_graph.add_edge(GraphNodeNames.REPHRASE_ANSWER, GraphNodeNames.POSTPROCESSING)
        self._state_graph.add_edge(GraphNodeNames.POSTPROCESSING, END)

    def _setup_graph(self):
        self._add_nodes()
        self._wire_graph()
        return self._state_graph.compile()
