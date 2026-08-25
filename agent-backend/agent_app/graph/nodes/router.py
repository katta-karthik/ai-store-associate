"""Intent Router Node for ShopAgent LangGraph."""

from typing import Dict, Any
from agent_app.schemas.agent_state import ShopAgentState


def intent_router_node(state: ShopAgentState) -> Dict[str, Any]:
    """Classify the incoming shopper query into an intent category."""
    query = state.user_query.lower().strip()

    wishlist_keywords = ["wishlist", "save for later", "save this", "favorite", "bookmark"]
    cart_keywords = [
        "cart", "add to cart", "bag", "add to bag", "basket", "checkout",
        "remove from cart", "delete from cart", "view cart", "show cart"
    ]
    compare_keywords = ["compare", "difference between", "which is better", " vs "]
    search_keywords = [
        "shoe", "shoes", "sneaker", "sneakers", "running", "trail", "under",
        "below", "price", "size", "nike", "adidas", "puma", "salomon", "look",
        "find", "show", "search", "buy", "recommend", "want", "need", "pair"
    ]

    if any(k in query for k in wishlist_keywords):
        intent = "wishlist_action"
    elif any(k in query for k in cart_keywords):
        intent = "cart_action"
    elif any(k in query for k in compare_keywords):
        intent = "compare_products"
    elif any(k in query for k in search_keywords):
        intent = "product_search"
    else:
        intent = "general_chat"

    return {"intent": intent}
