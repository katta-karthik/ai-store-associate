"""Product Comparison & Fit Advisor Node for ShopAgent LangGraph."""

import re
from typing import Any, Dict, List, Optional
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState, UIAction
from agent_app.tools.store_tools import store_client


async def product_comparator_node(state: ShopAgentState) -> Dict[str, Any]:
    """Perform side-by-side technical comparison and formulate consultative verdict."""
    query = state.user_query.lower()
    
    # 1. Fetch all products to match against
    all_res = await store_client.search_products(ExtractedFilters())
    all_products = all_res.get("items", [])

    matched_products: List[Dict[str, Any]] = []

    # Check for matched product names in query
    for p in all_products:
        title_lower = p["title"].lower()
        brand_lower = p["brand"].lower()
        # Check matching tokens
        if any(part in query for part in title_lower.split() if len(part) > 3) or brand_lower in query:
            if p not in matched_products:
                matched_products.append(p)

    # If fewer than 2 matched from specific terms, pick top 2 most relevant
    if len(matched_products) < 2 and len(all_products) >= 2:
        for p in all_products:
            if p not in matched_products:
                matched_products.append(p)
            if len(matched_products) == 2:
                break

    if len(matched_products) >= 2:
        p1 = matched_products[0]
        p2 = matched_products[1]

        # Extract specs with fallbacks
        p1_specs = p1.get("specs", {})
        p2_specs = p2.get("specs", {})

        p1_cushion = p1_specs.get("cushioning", "Standard EVA")
        p2_cushion = p2_specs.get("cushioning", "Standard EVA")
        p1_weight = p1_specs.get("weight", "285g")
        p2_weight = p2_specs.get("weight", "295g")
        p1_drop = p1_specs.get("heel_drop", "10mm")
        p2_drop = p2_specs.get("heel_drop", "10mm")

        # Fit guidance
        fit_note = ""
        if "salomon" in p1["brand"].lower() or "salomon" in p2["brand"].lower():
            fit_note = "\n\n💡 **Fit Advice**: Salomon shoes have a technical athletic fit—if you prefer a roomier toe box, we recommend going **half a size up**."

        # Consultative Comparison Narrative
        response_text = (
            f"⚖️ **Side-by-Side Comparison: {p1['title']} vs {p2['title']}**\n\n"
            f"• **{p1['title']}** (₹{p1['base_price']:,.0f}): Engineered with **{p1_cushion}** ({p1_weight}, {p1_drop} drop). Best for high-mileage durability and balanced support.\n"
            f"• **{p2['title']}** (₹{p2['base_price']:,.0f}): Features **{p2_cushion}** ({p2_weight}, {p2_drop} drop). Exceptional energy return and premium comfort.\n\n"
            f"🏁 **Salesperson Verdict**: Choose **{p1['title']}** for daily training dependability, or **{p2['title']}** for maximum energy bounce and plush step-in feel.{fit_note}"
        )

        ui_actions = [
            UIAction(
                action="OPEN_COMPARISON_MODAL",
                payload={"products": [p1, p2]},
            ),
            UIAction(
                action="HIGHLIGHT_PRODUCTS",
                payload={"product_ids": [p1["id"], p2["id"]]},
            ),
        ]

        return {
            "final_response": response_text,
            "ui_actions": ui_actions,
        }

    return {
        "final_response": "I'd be glad to compare shoes for you! Tell me which two models or brands you are evaluating (e.g. *'Compare Nike Pegasus vs Adidas Ultraboost'*).",
        "ui_actions": [],
    }
