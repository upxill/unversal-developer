from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import coder_node, reviewer_node, unit_tester_node, file_saver_node


def should_continue(state: AgentState):
    if (state["is_passing"] and not state["feedback"]) or state["iterations"] >= 3:
        return "save"
    return "coder"


def create_graph():
    builder = StateGraph(AgentState)

    builder.add_node("coder", coder_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("unit_tester", unit_tester_node)
    builder.add_node("file_saver", file_saver_node)

    builder.set_entry_point("coder")
    builder.add_edge("coder", "reviewer")
    builder.add_edge("reviewer", "unit_tester")

    builder.add_conditional_edges(
        "unit_tester", should_continue, {"coder": "coder", "save": "file_saver"}
    )
    builder.add_edge("file_saver", END)

    return builder.compile()
