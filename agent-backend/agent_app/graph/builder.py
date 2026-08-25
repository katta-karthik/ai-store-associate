"""LangGraph State Graph Builder for ShopAgent."""

from langgraph.graph import END, StateGraph
from agent_app.graph.nodes.cart_manager import cart_manager_node
from agent_app.graph.nodes.deep_research import deep_research_node
from agent_app.graph.nodes.memory_loader import memory_loader_node
from agent_app.graph.nodes.product_comparator import product_comparator_node
from agent_app.graph.nodes.router import intent_router_node
from agent_app.graph.nodes.salesperson_responder import salesperson_responder_node
from agent_app.graph.nodes.search_extractor import search_extractor_node
from agent_app.schemas.agent_state import ShopAgentState


def _route_next_step(state: ShopAgentState) -> str:
    """Conditional router determining next node in graph."""
    if state.intent == "product_search":
        return "search_extractor"
    elif state.intent in ("cart_action", "wishlist_action"):
        return "cart_manager"
    elif state.intent == "compare_products":
        return "product_comparator"
    elif state.intent == "deep_research":
        return "deep_research"
    return "salesperson_responder"


def build_shopagent_graph():
    """Compile the LangGraph state graph for ShopAgent with memory, comparison, and deep research."""
    workflow = StateGraph(ShopAgentState)

    # 1. Register Nodes
    workflow.add_node("memory_loader", memory_loader_node)
    workflow.add_node("router", intent_router_node)
    workflow.add_node("search_extractor", search_extractor_node)
    workflow.add_node("salesperson_responder", salesperson_responder_node)
    workflow.add_node("cart_manager", cart_manager_node)
    workflow.add_node("product_comparator", product_comparator_node)
    workflow.add_node("deep_research", deep_research_node)

    # 2. Set Entry Point to Memory Loader
    workflow.set_entry_point("memory_loader")
    workflow.add_edge("memory_loader", "router")

    # 3. Add Conditional Transitions
    workflow.add_conditional_edges(
        "router",
        _route_next_step,
        {
            "search_extractor": "search_extractor",
            "cart_manager": "cart_manager",
            "product_comparator": "product_comparator",
            "deep_research": "deep_research",
            "salesperson_responder": "salesperson_responder",
        },
    )

    # 4. Add Linear Transitions
    workflow.add_edge("search_extractor", "salesperson_responder")
    workflow.add_edge("salesperson_responder", END)
    workflow.add_edge("cart_manager", END)
    workflow.add_edge("product_comparator", END)
    workflow.add_edge("deep_research", END)

    return workflow.compile()


# Pre-compiled graph instance
shopagent_app = build_shopagent_graph()
