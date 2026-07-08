"""Agentic tutoring pipeline built with LangGraph + LangChain (Claude).

The graph runs three stages in sequence:

    analyze  ->  tutor  ->  followup

  * analyze  — classifies the subject / concepts / difficulty of the question
  * tutor    — produces an adaptive, step-by-step explanation
  * followup — proposes practice questions to reinforce the concept

Each stage is a node that calls Claude (`claude-opus-4-8`) through
`langchain-anthropic`. State is passed between nodes as a typed dict.
"""

from typing import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.core.config import settings

_llm: ChatAnthropic | None = None


def _get_llm() -> ChatAnthropic:
    """Lazily construct the Claude chat model so the app can boot without a key."""
    global _llm
    if _llm is None:
        kwargs: dict = {"model": settings.llm_model, "max_tokens": 2048, "timeout": 60}
        if settings.anthropic_api_key:
            kwargs["api_key"] = settings.anthropic_api_key
        _llm = ChatAnthropic(**kwargs)
    return _llm


def _text(message: BaseMessage) -> str:
    """Normalise a chat message's content to a plain string."""
    content = message.content
    if isinstance(content, str):
        return content.strip()
    parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "".join(parts).strip()


class TutorState(TypedDict):
    question: str
    student_name: str
    analysis: str
    answer: str
    followups: list[str]


async def analyze_node(state: TutorState) -> dict:
    messages = [
        SystemMessage(
            content=(
                "You are the analysis stage of an adaptive AI tutor. Given a student's "
                "question, identify the subject area, the key concepts involved, and "
                "estimate the difficulty level (beginner, intermediate, or advanced). "
                "Answer in 2-3 concise sentences."
            )
        ),
        HumanMessage(content=state["question"]),
    ]
    resp = await _get_llm().ainvoke(messages)
    return {"analysis": _text(resp)}


async def tutor_node(state: TutorState) -> dict:
    messages = [
        SystemMessage(
            content=(
                "You are an adaptive AI tutor. Teach the student by explaining clearly and "
                "adapting to the difficulty implied by the analysis. Use a friendly, "
                "encouraging tone, give step-by-step reasoning, and include a concrete "
                "example where it helps. Address the student by name "
                f"({state['student_name']}).\n\n"
                f"Question analysis: {state['analysis']}"
            )
        ),
        HumanMessage(content=state["question"]),
    ]
    resp = await _get_llm().ainvoke(messages)
    return {"answer": _text(resp)}


async def followup_node(state: TutorState) -> dict:
    messages = [
        SystemMessage(
            content=(
                "Based on the tutoring answer, suggest exactly 3 short follow-up practice "
                "questions that reinforce the concept. Return each question on its own line "
                "with no numbering or bullet characters."
            )
        ),
        HumanMessage(content=f"Question: {state['question']}\n\nAnswer given:\n{state['answer']}"),
    ]
    resp = await _get_llm().ainvoke(messages)
    lines = [line.strip(" -•*\t").strip() for line in _text(resp).splitlines()]
    followups = [line for line in lines if line]
    return {"followups": followups[:3]}


def _build_graph():
    graph = StateGraph(TutorState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("tutor", tutor_node)
    graph.add_node("followup", followup_node)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "tutor")
    graph.add_edge("tutor", "followup")
    graph.add_edge("followup", END)
    return graph.compile()


_app = _build_graph()


async def run_tutor_pipeline(question: str, student_name: str) -> dict:
    result = await _app.ainvoke({"question": question, "student_name": student_name})
    return {
        "analysis": result["analysis"],
        "answer": result["answer"],
        "followups": result["followups"],
    }
