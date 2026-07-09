"""Assemble the supervisor-routed multi-agent tutor graph.

    START -> supervisor -(route)-> worker -> supervisor -> ... -> END

The supervisor is a passthrough node; `route` (router.py) decides the next agent
based on which state fields are filled, matching the guide's conditional edges.
"""

from langgraph.graph import END, START, StateGraph

from app.features.tutor.graph.nodes.diagnostic import diagnostic_node
from app.features.tutor.graph.nodes.escalation import escalation_node
from app.features.tutor.graph.nodes.evaluator import evaluator_node
from app.features.tutor.graph.nodes.guard import guard_node
from app.features.tutor.graph.nodes.hint import hint_node
from app.features.tutor.graph.nodes.memory import memory_node
from app.features.tutor.graph.nodes.misconception import misconception_node
from app.features.tutor.graph.nodes.planner import planner_node
from app.features.tutor.graph.nodes.profile import profile_node
from app.features.tutor.graph.nodes.revision import revision_node
from app.features.tutor.graph.router import route
from app.features.tutor.graph.state import TutorState


async def _supervisor(state: TutorState, config) -> dict:
    return {}


def build_graph():
    graph = StateGraph(TutorState)

    graph.add_node("supervisor", _supervisor)
    graph.add_node("profile", profile_node)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("misconception", misconception_node)
    graph.add_node("planner", planner_node)
    graph.add_node("hint", hint_node)
    graph.add_node("guard", guard_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("memory", memory_node)
    graph.add_node("revision", revision_node)
    graph.add_node("escalation", escalation_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route,
        {
            "profile": "profile",
            "diagnostic": "diagnostic",
            "misconception": "misconception",
            "planner": "planner",
            "hint": "hint",
            "evaluator": "evaluator",
            "memory": "memory",
            "escalation": "escalation",
            "await": END,
        },
    )

    # Workers return to the supervisor to be re-routed.
    for node in ["profile", "diagnostic", "misconception", "planner", "evaluator"]:
        graph.add_edge(node, "supervisor")
    graph.add_edge("hint", "guard")
    graph.add_edge("guard", "supervisor")

    # Terminal branches.
    graph.add_edge("memory", "revision")
    graph.add_edge("revision", END)
    graph.add_edge("escalation", END)

    return graph.compile()


tutor_graph = build_graph()
