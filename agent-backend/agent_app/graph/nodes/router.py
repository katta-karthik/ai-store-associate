"""Intent Router Node for ShopAgent LangGraph v3.0.

Primary: LLM-powered multi-intent classification with conversation history awareness.
Fallback: Enhanced keyword & pattern matching when LLM is unavailable.
"""

import logging
from typing import Dict, Any
from agent_app.core.llm_client import llm_client
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import ShopAgentState

logger = logging.getLogger("shopagent.router")


async def intent_router_node(state: ShopAgentState) -> Dict[str, Any]:
    """Classify the incoming shopper query into an intent category with contextual follow-up awareness."""
    query = state.user_query.strip()
    q_lower = query.lower()

    # 1. Primary AI Intent Classification
    if llm_client.is_available and query:
        try:
            profile_context = ""
            if state.shopper_profile and hasattr(state.shopper_profile, "get_personalization_context"):
                profile_context = state.shopper_profile.get_personalization_context()

            history_text = ""
            if state.conversation_history:
                history_text = conversation_store.format_history_for_llm(state.conversation_history, max_turns=6)

            ai_result = await llm_client.classify_intent(
                query=query,
                conversation_history=history_text,
                profile_context=profile_context,
            )

            if ai_result and "intent" in ai_result:
                intent = ai_result["intent"]
                confidence = float(ai_result.get("confidence", 0.95))
                # Validate intent is recognized
                valid_intents = {
                    "product_search", "cart_action", "wishlist_action",
                    "compare_products", "deep_research", "gift_recommendation",
                    "style_advice", "follow_up", "reorder", "general_chat",
                }
                if intent in valid_intents:
                    return {
                        "intent": intent,
                        "intent_confidence": confidence,
                    }
        except Exception as e:
            logger.warning(f"AI intent classification failed: {e}. Using rule fallback.")

    # 2. Rule-Based Fallback
    deep_research_keywords = [
        "flat feet", "overpronation", "supination", "knee pain", "joint pain", "first marathon",
        "training for", "best shoe for someone", "road and trail", "hybrid run",
        "deep research", "critique", "which shoe should i get for marathon", "plantar fasciitis",
        "biomechanics", "pronation", "cushioning tech"
    ]
    wishlist_keywords = ["wishlist", "save for later", "save this", "favorite", "bookmark"]
    cart_keywords = [
        "cart", "add to cart", "bag", "add to bag", "basket", "checkout",
        "remove from cart", "delete from cart", "view cart", "show cart", "buy this", "order now"
    ]
    compare_keywords = [
        "compare", "difference between", "which is better", " vs ", " versus ",
        "side by side", "better for", "how do they compare", "which one should i get",
        "which is lighter", "which is more comfortable"
    ]
    follow_up_keywords = [
        "something cheaper", "cheaper", "more expensive", "in black", "in white",
        "other colors", "different color", "another option", "show more", "first one",
        "second one", "that pair", "the first shoe", "alternative"
    ]
    search_keywords = [
        "shoe", "shoes", "sneaker", "sneakers", "running", "trail", "under",
        "below", "price", "size", "nike", "adidas", "puma", "salomon", "look",
        "find", "show", "search", "buy", "recommend", "want", "need", "pair",
        "cheaper", "expensive", "black", "white", "more options", "asics", "hoka"
    ]

    if any(k in q_lower for k in deep_research_keywords):
        intent = "deep_research"
    elif any(k in q_lower for k in compare_keywords):
        intent = "compare_products"
    elif any(k in q_lower for k in wishlist_keywords):
        intent = "wishlist_action"
    elif any(k in q_lower for k in cart_keywords):
        intent = "cart_action"
    elif any(k in q_lower for k in follow_up_keywords) and state.conversation_history:
        intent = "product_search"  # Route follow_ups to search_extractor with context
    elif any(k in q_lower for k in search_keywords):
        intent = "product_search"
    else:
        intent = "general_chat"

    return {
        "intent": intent,
        "intent_confidence": 0.85,
    }
