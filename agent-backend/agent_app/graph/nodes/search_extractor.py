"""Search & Entity Extraction Node for ShopAgent LangGraph v3.0.

Primary: LLM-powered entity & constraint extraction with multi-turn memory.
Fallback: Robust regex & rule-based parameter extraction.
"""

import re
import logging
from typing import Any, Dict
from agent_app.core.llm_client import llm_client
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState
from agent_app.tools.store_tools import store_client

logger = logging.getLogger("shopagent.search_extractor")


async def search_extractor_node(state: ShopAgentState) -> Dict[str, Any]:
    """Extract search parameters from user query and fetch matching products from Store API."""
    query_text = state.user_query.strip()
    q_lower = query_text.lower()
    profile = state.shopper_profile
    filters = ExtractedFilters()
    follow_up_context = None

    # 1. Primary AI Entity Extraction
    extracted_by_ai = False
    if llm_client.is_available and query_text:
        try:
            profile_context = profile.get_personalization_context() if profile else ""
            history_text = ""
            if state.conversation_history:
                history_text = conversation_store.format_history_for_llm(state.conversation_history, max_turns=6)

            ai_entities = await llm_client.extract_entities(
                query=query_text,
                profile_context=profile_context,
                conversation_history=history_text,
            )

            if ai_entities:
                if ai_entities.get("category_id"):
                    filters.category_id = ai_entities["category_id"]
                if ai_entities.get("min_price") is not None:
                    filters.min_price = float(ai_entities["min_price"])
                if ai_entities.get("max_price") is not None:
                    filters.max_price = float(ai_entities["max_price"])
                if ai_entities.get("brand"):
                    filters.brand = str(ai_entities["brand"]).capitalize()
                if ai_entities.get("size"):
                    filters.size = str(ai_entities["size"])
                if ai_entities.get("color"):
                    filters.color = str(ai_entities["color"]).lower()
                if ai_entities.get("occasion"):
                    filters.occasion = str(ai_entities["occasion"])
                if ai_entities.get("use_case"):
                    filters.use_case = str(ai_entities["use_case"])
                if ai_entities.get("query"):
                    filters.query = str(ai_entities["query"])

                extracted_by_ai = True
        except Exception as e:
            logger.warning(f"AI entity extraction failed: {e}. Falling back to regex.")

    # 2. Rule & Regex Extraction (if AI not available or partial)
    if not extracted_by_ai:
        # Price extraction
        price_match = re.search(r'(?:under|below|less than|within|around)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?', q_lower)
        if price_match:
            val = float(price_match.group(1))
            if price_match.group(2) in ["k", "thousand"]:
                val *= 1000
            filters.max_price = val
        elif profile and profile.budget_max:
            filters.max_price = profile.budget_max

        # Size extraction
        size_match = re.search(r'(?:size|uk|us)\s*(\d+)', q_lower)
        if size_match:
            filters.size = size_match.group(1)
        elif profile and profile.preferred_size:
            filters.size = profile.preferred_size

        # Brand extraction
        known_brands = ["nike", "adidas", "puma", "salomon", "asics", "hoka", "new balance"]
        for b in known_brands:
            if b in q_lower:
                filters.brand = b.capitalize()
                break

        # Category extraction
        if any(k in q_lower for k in ["trail", "outdoor", "hiking", "mud", "waterproof", "gore-tex"]):
            filters.category_id = "trail-outdoor"
        elif any(k in q_lower for k in ["run", "running", "marathon", "road", "jog"]):
            filters.category_id = "running-shoes"
        elif any(k in q_lower for k in ["sneaker", "casual", "streetwear", "retro", "lifestyle"]):
            filters.category_id = "lifestyle-sneakers"

        # Residual text
        if not filters.brand and not filters.category_id:
            clean_q = re.sub(r'(?:under|below|less than)\s*\d+k?', '', q_lower).strip()
            if clean_q:
                filters.query = clean_q

    # 3. Contextual Enrichment & Follow-up Refinements
    if "cheaper" in q_lower or "less expensive" in q_lower:
        follow_up_context = "User requested more affordable options compared to prior recommendations."
        if filters.max_price:
            filters.max_price = filters.max_price * 0.85
        elif profile and profile.budget_max:
            filters.max_price = profile.budget_max * 0.85
        else:
            filters.max_price = 8000.0

    # Auto-apply preferred size from profile if not explicitly extracted
    if not filters.size and profile and profile.preferred_size:
        filters.size = profile.preferred_size

    # Auto-apply preferred brand if query has no brand and user has strong brand affinity
    if not filters.brand and profile and profile.preferred_brands and len(profile.preferred_brands) == 1:
        # If user specifically asked for category without specifying brand, or general query
        if not filters.query:
            filters.brand = profile.preferred_brands[0]

    # Execute Search via Universal Store API
    search_res = await store_client.search_products(filters)
    items = search_res.get("items", [])

    # If strict filter returned 0 results, retry with relaxed query (e.g., relax brand or price)
    if not items and (filters.brand or filters.max_price):
        relaxed_filters = filters.model_copy()
        relaxed_filters.brand = None
        fallback_res = await store_client.search_products(relaxed_filters)
        items = fallback_res.get("items", [])

    return {
        "extracted_filters": filters,
        "retrieved_products": items,
        "follow_up_context": follow_up_context,
    }
