"""Module for the AnswerGraphState class."""

import operator
from typing import Annotated

from typing_extensions import TypedDict


class GraphState(TypedDict):

    question: str | None
    history: list[tuple[str, str]]
    raw_answer: str | None
    processed_answer: str | None
    question_language: str | None
    additional_info: dict
    error_messages: Annotated[list[str], operator.add]
    finish_reasons: Annotated[list[str], operator.add]

    @classmethod
    def create(
        cls,
        history: list[tuple[str, str]],
        question: str | str = None,
        raw_answer: str | None = None,
        processed_answer: str | None = None,
        question_language: str | None = None,
        additional_info: dict | None = None,
        error_messages: list[str] | None = None,
        finish_reasons: list[str] | None = None,
    ) -> "GraphState":
        return GraphState(
            question=question,
            history=history,
            raw_answer=raw_answer,
            processed_answer=processed_answer,
            question_language=question_language,
            additional_info=additional_info if additional_info else {},
            error_messages=error_messages if error_messages else [],
            finish_reasons=finish_reasons if finish_reasons else [],
        )
