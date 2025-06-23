"""Module for the string enum class GraphNodeNames and the DefaultChatGraph class."""

import io
import logging
from enum import StrEnum
from pathlib import Path
from time import time
from tkinter import Image
from typing import Any, Optional

import inject
from langchain_core.runnables.base import RunnableSequence
from langdetect import detect
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import END, START, StateGraph
from langchain_core.language_models.chat_models import BaseChatModel

from assistant.impl.graph.graph_state import GraphState

logger = logging.getLogger(__name__)


class GraphNodeNames(StrEnum):

    REPHRASE_QUESTION = "rephrase_question"
    DETERMINE_LANGUAGE = "determine_language"
    DECIDE = "decide"
    ERROR_NODE = "error_node"
    REPHRASE_ANSWER = "rephrase_answer"
    ADD_ADDITIONAL_INFORMATION = "add_additional_information"


class ChatGraph:

    @inject.params(
        llm=BaseChatModel,
        question_rephraser="question_rephraser",
        answer_rephraser="answer_rephraser",
        mcp_agent="mcp_agent",
    )
    def __init__(
        self,
        llm: BaseChatModel,
        question_rephraser: RunnableSequence,
        answer_rephraser: RunnableSequence,
        mcp_agent: RunnableSequence,
    ):

        self._question_rephraser = question_rephraser
        self._answer_rephraser = answer_rephraser
        self._llm = llm
        self._mcp_agent = mcp_agent
        self._state_graph = StateGraph(GraphState)
        self._graph = self._setup_graph()

    async def ainvoke(
        self, graph_input: list[tuple[str, str]], config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        if not graph_input:
            return ""

        state = GraphState.create(
            history=graph_input,
        )

        logger.info("RECEIVED question: %s", state["question"])

        response_state = await self._graph.ainvoke(input=state, config=config)

        logger.info("GENERATED answer: %s", response_state["processed_answer"])

        return response_state["processed_answer"]

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
        img = Image.open(
            io.BytesIO(
                self._graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
        )
        if relative_dir_path:
            p = Path.cwd() / relative_dir_path
        else:
            p = Path.cwd()

        p.mkdir(parents=True, exist_ok=True)
        img.save(p / f"graph_{str(time()).replace('.', '_')}.png")

    #########
    # nodes #
    #########
    async def _determine_language_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question = state["history"][-1][1]  # TODO: ensure this exists
        question_language = detect(question)
        logger.info('Detected langauge for question "%s": %s', question, question_language)
        return {"question_language": question_language}

    async def _rephrase_question_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question = state["history"][-1][1]  # TODO: ensure this exists
        history = [f"{message[0]}: {message[1]}" for message in state["history"][0:-1]]

        rephrased_question = await self._question_rephraser.ainvoke({"question": question, "history": history}, config)
        rephrased_question = rephrased_question.content
        logger.info('Rephrased question "%s" with history "%s" to %s', question, history, rephrased_question)
        return {"question": rephrased_question}

    async def _answer_rephraser_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        rephrased_answer = await self._answer_rephraser.ainvoke(state, config)
        rephrased_answer = rephrased_answer.content
        return {"processed_answer": rephrased_answer}

    async def _decide_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        answer = await self._mcp_agent.ainvoke({"messages": state["question"]}, config)
        answer = answer["messages"][-1].content
        return {"raw_answer": answer}

    async def _add_additional_information_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        # TODO: add additional information about the user that was inferred by previous interactions
        return {}

    async def _error_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        logger.error("\n".join(state["error_messages"]))
        return {
            "processed_answer": "I'm sorry, there have been some errors and your request could not be handled. "
            + f"Errors: {'\n'.join(state['error_messages'])}"
        }

    #####################
    # conditional edges #
    #####################

    def _add_nodes(self):
        self._state_graph.add_node(GraphNodeNames.REPHRASE_QUESTION, self._rephrase_question_node)
        self._state_graph.add_node(GraphNodeNames.DETERMINE_LANGUAGE, self._determine_language_node)
        self._state_graph.add_node(GraphNodeNames.DECIDE, self._decide_node)
        self._state_graph.add_node(GraphNodeNames.ERROR_NODE, self._error_node)
        self._state_graph.add_node(GraphNodeNames.REPHRASE_ANSWER, self._answer_rephraser_node)
        self._state_graph.add_node(GraphNodeNames.ADD_ADDITIONAL_INFORMATION, self._add_additional_information_node)

    def _wire_graph(self):
        self._state_graph.add_edge(START, GraphNodeNames.DETERMINE_LANGUAGE)
        self._state_graph.add_edge(START, GraphNodeNames.REPHRASE_QUESTION)
        self._state_graph.add_edge(GraphNodeNames.REPHRASE_QUESTION, GraphNodeNames.ADD_ADDITIONAL_INFORMATION)
        self._state_graph.add_edge(GraphNodeNames.ADD_ADDITIONAL_INFORMATION, GraphNodeNames.DECIDE)
        self._state_graph.add_edge(
            [GraphNodeNames.DECIDE, GraphNodeNames.DETERMINE_LANGUAGE], GraphNodeNames.REPHRASE_ANSWER
        )
        self._state_graph.add_edge(GraphNodeNames.REPHRASE_ANSWER, END)
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)

    def _setup_graph(self):
        self._add_nodes()
        self._wire_graph()
        return self._state_graph.compile()
