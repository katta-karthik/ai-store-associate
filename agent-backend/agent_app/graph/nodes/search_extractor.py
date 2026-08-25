"""Search & Entity Extraction Node for ShopAgent LangGraph."""

import re
from typing import Any, Dict
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState
from agent_app.tools.store_tools import store_client


async def search_extractor_node(state: ShopAgentState) -> Dict[str, Any]:
    """Extract search parameters from user query and fetch matching products from Store API."""
    query_text = state.user_query.lower()
    filters = ExtractedFilters()

    # 1. Price extraction (e.g. "under 8000", "under 8k", "below 7500", "less than 8000")
    price_match = re.search(r'(?:under|below|less than|within)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?', query_text)
    if price_match:
        val = float(price_match.group(1))
        if price_match.group(2) in ["k", "thousand"]:
            val *= 1000
        filters.max_price = val

    # 2. Size extraction (e.g. "size 10", "size 9", "uk 10", "us 10")
    size_match = re.search(r'(?:size|uk|us)\s*(\d+)', query_text)
    if size_match:
        filters.size = size_match.group(1)

    # 3. Brand extraction
    known_brands = ["nike", "adidas", "puma", "salomon"]
    for b in known_brands:
        if b in query_text:
            filters.brand = b.capitalize()
            break

    # 4. Category extraction
    if any(k in query_text for k in ["trail", "outdoor", "hiking", "mud"]):
        filters.category_id = "trail-outdoor"
    elif any(k in query_text for k in ["run", "running", "marathon", "road"]):
        filters.category_id = "running-shoes"
    elif any(k in query_text for k in ["sneaker", "casual", "streetwear", "retro", "lifestyle"]):
        filters.category_id = "lifestyle-sneakers"

    # 5. Extract residual query terms if no specific brand or category
    if not filters.brand and not filters.category_id:
        clean_q = re.sub(r'(?:under|below|less than)\s*\d+k?', '', query_text).strip()
        if clean_q:
            filters.query = clean_q

    # Execute Search via Universal Store API
    search_res = await store_client.search_products(filters)
    items = search_res.get("items", [])

    return {
        "extracted_filters": filters,
        "retrieved_products": items,
    }
