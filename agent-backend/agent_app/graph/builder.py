"""LangGraph State Graph Builder for ShopAgent."""

from langgraph.graph import END, StateGraph
from agent_app.graph.nodes.router import intent_router_node
from agent_app.graph.nodes.salesperson_responder import salesperson_responder_node
from agent_app.graph.nodes.search_extractor import search_extractor_node
from agent_app.schemas.agent_state import ShopAgentState


def _route_next_step(state: ShopAgentState) -> str:
    """Conditional router determining next node in graph."""
    if state.intent == "product_search":
        return "search_extractor"
    return "salesperson_responder"


def build_shopagent_graph():
    """Compile the LangGraph state graph for ShopAgent."""
    workflow = StateGraph(ShopAgentState)

    # 1. Register Nodes
    workflow.add_node("router", intent_router_node)
    workflow.add_node("search_extractor", search_extractor_node)
    workflow.add_node("salesperson_responder", salesperson_responder_node)

    # 2. Set Entry Point
    workflow.set_entry_point("router")

    # 3. Add Conditional Transitions
    workflow.add_conditional_edges(
        "router",
        _route_next_step,
        {
            "search_extractor": "search_extractor",
            "salesperson_responder": "salesperson_responder",
        },
    )

    # 4. Add Linear Transitions
    workflow.add_edge("search_extractor", "salesperson_responder")
    workflow.add_edge("salesperson_responder", END)

    return workflow.compile()


# Pre-compiled graph instance
shopagent_app = build_shopagent_graph()
