"""Intent Router Node for ShopAgent LangGraph."""

from typing import Dict, Any
from agent_app.schemas.agent_state import ShopAgentState


def intent_router_node(state: ShopAgentState) -> Dict[str, Any]:
    """Classify the incoming shopper query into an intent category."""
    query = state.user_query.lower().strip()

    # Fast heuristic classification
    search_keywords = [
        "shoe", "shoes", "sneaker", "sneakers", "running", "trail", "under",
        "below", "price", "size", "nike", "adidas", "puma", "salomon", "look",
        "find", "show", "search", "buy", "recommend", "want", "need", "pair"
    ]
    cart_keywords = ["cart", "add to cart", "buy this", "checkout"]
    compare_keywords = ["compare", "difference between", "which is better", "vs"]

    if any(k in query for k in compare_keywords):
        intent = "compare_products"
    elif any(k in query for k in cart_keywords):
        intent = "cart_action"
    elif any(k in query for k in search_keywords):
        intent = "product_search"
    else:
        intent = "general_chat"

    return {"intent": intent}
