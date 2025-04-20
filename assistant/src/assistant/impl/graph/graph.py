"""Module for the string enum class GraphNodeNames and the DefaultChatGraph class."""

import io
import logging
from enum import StrEnum
from functools import partial
from pathlib import Path
from time import time
from tkinter import Image
from typing import Any, Optional

from langchain_core.prompts import PromptTemplate
from langdetect import detect
from assistant.impl.graph.graph_state import GraphState
from fastapi import HTTPException, status
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import END, START, StateGraph


logger = logging.getLogger(__name__)


class GraphNodeNames(StrEnum):

    REPHRASE_QUESTION = "rephrase_question"
    DETERMINE_LANGUAGE = "determine_language"
    DECIDE = "decide"
    ERROR_NODE = "error_node"
    REPHRASE_ANSWER = "rephrase_answer"
    ADD_ADDITIONAL_INFORMATION = "add_additional_information"


class DefaultChatGraph:

    def __init__(
        self,
        llm,
    ):
        rephrase_question_prompt = PromptTemplate.from_template("""
Rephrase the question so it containts all the relevant information from the history required to answer the question.
                                                       
                                                       Question: {question}
                                                       History: {history}
                                                       """) # TODO: don't do this here. Also make it adjustable
        
        self._question_rephraser = rephrase_question_prompt | llm
        rephrase_answer_prompt = PromptTemplate.from_template("""
                                                              You are James, a butler of the aristocracy. You were told to do {question}. You determined that the correct answer is {raw_answer}.
                                                              Rephrase this answer. Answer in the following language: {question_language}.
                                                       """) # TODO: don't do this here. Also make it adjustable
        
        self._question_rephraser = rephrase_question_prompt | llm
        self._answer_rephraser = rephrase_answer_prompt | llm
        self._state_graph = StateGraph(GraphState)
        self._rephrase_node_builder = partial(self._rephrase_node)
        self._generate_node_builder = partial(self._generate_node)
        self._graph = self._setup_graph()

    async def ainvoke(
        self, graph_input: list[tuple[str,str]], config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:      
        if not graph_input:
            return ""
        

        state = GraphState.create(
            history=graph_input,            
        )

        #logger.info("RECEIVED question: %s", state["question"])

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
        question = state["history"][-1][1] # TODO: ensure this exists
        question_language = detect(question)
        logger.info("Detected langauge for question \"%s\": %s",question, question_language)
        return {"question_language": question_language}
    
    async def _rephrase_question_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        question = state["history"][-1][1] # TODO: ensure this exists
        history = [f"{message[0]}: {message[1]}" for message in state["history"][0:-1]]

        rephrased_question = await self._question_rephraser.ainvoke({"question":question,history:history}, config)

        logger.info("Rephrased question \"%s\" with history \"%s\" to %s",question, history, rephrased_question)
        return {"question": rephrased_question}

    async def _answer_rephraser_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        rephrased_answer = await self._answer_rephraser.ainvoke(state, config)
        return {"processed_answer": rephrased_answer}

    async def _decide_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        # TODO: use mcp to allow the llm to answer the question/perform the required tasks
        return {}

    async def _add_additional_information_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        # TODO: add additional information about the user that was inferred by previous interactions
        return {}

    async def _error_node(self, state: dict, config: Optional[RunnableConfig] = None) -> dict:
        logger.error('\n'.join([x for x in state['error_messages']]))
        return {"processed_answer": f"I'm sorry, there have been some errors and your request could not be handled. Errors: {'\n'.join([x for x in state['error_messages']])}"}

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
        self._state_graph.add_edge([GraphNodeNames.DECIDE, GraphNodeNames.DETERMINE_LANGUAGE], GraphNodeNames.REPHRASE_ANSWER)
        self._state_graph.add_edge(GraphNodeNames.REPHRASE_ANSWER, END)
        self._state_graph.add_edge(GraphNodeNames.ERROR_NODE, END)