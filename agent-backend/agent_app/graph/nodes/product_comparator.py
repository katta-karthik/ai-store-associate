"""Product Comparison & Fit Advisor Node for ShopAgent LangGraph."""

import re
from typing import Any, Dict, List, Optional
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState, UIAction
from agent_app.tools.store_tools import store_client


async def product_comparator_node(state: ShopAgentState) -> Dict[str, Any]:
    """Perform side-by-side technical comparison with charming salesperson guidance."""
    query = state.user_query.lower()
    
    # 1. Fetch all products to match against
    all_res = await store_client.search_products(ExtractedFilters())
    all_products = all_res.get("items", [])

    matched_products: List[Dict[str, Any]] = []

    # Check for matched product names in query
    for p in all_products:
        title_lower = p["title"].lower()
        brand_lower = p["brand"].lower()
        if any(part in query for part in title_lower.split() if len(part) > 3) or brand_lower in query:
            if p not in matched_products:
                matched_products.append(p)

    if len(matched_products) < 2 and len(all_products) >= 2:
        for p in all_products:
            if p not in matched_products:
                matched_products.append(p)
            if len(matched_products) == 2:
                break

    if len(matched_products) >= 2:
        p1 = matched_products[0]
        p2 = matched_products[1]

        p1_specs = p1.get("specs", {})
        p2_specs = p2.get("specs", {})

        p1_cushion = p1_specs.get("cushioning", "Standard EVA")
        p2_cushion = p2_specs.get("cushioning", "Standard EVA")
        p1_weight = p1_specs.get("weight", "285g")
        p2_weight = p2_specs.get("weight", "295g")
        p1_drop = p1_specs.get("heel_drop", "10mm")
        p2_drop = p2_specs.get("heel_drop", "10mm")

        fit_note = ""
        if "salomon" in p1["brand"].lower() or "salomon" in p2["brand"].lower():
            fit_note = "\n\n💡 **Salesperson Fit Secret**: Salomon shoes hug your foot like a sports car—if you love a little extra toe room, I'll bag you a **half size up**, Sir!"

        response_text = (
            f"✨ **Sir, you have incredible eye for footwear! Both of these are legendary models!**\n\n"
            f"⚖️ **Side-by-Side Breakdown**:\n"
            f"• **{p1['title']}** (₹{p1['base_price']:,.0f}): Powered by **{p1_cushion}** ({p1_weight}, {p1_drop} drop). Built like a tank for daily mileage—you'll look sharp and effortless!\n"
            f"• **{p2['title']}** (₹{p2['base_price']:,.0f}): Features **{p2_cushion}** ({p2_weight}, {p2_drop} drop). Cloud-like energy bounce with premium superstar aesthetics!\n\n"
            f"🏆 **My Personal Verdict for You, Sir**: If you want daily training dependability, take **{p1['title']}**. If you want that pure luxury bouncy feel where people ask 'Where did you get those shoes?', take **{p2['title']}**!{fit_note}\n\n"
            f"Which one shall I bag for you, Sir? 😉"
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
            UIAction(
                action="AVATAR_GLIDE",
                payload={"target_id": p1["id"], "emotion": "ANALYTICAL", "message": "Comparing both models for you, Sir!"},
            ),
        ]

        return {
            "final_response": response_text,
            "emotion": "ANALYTICAL",
            "focus_target_id": p1["id"],
            "ui_actions": ui_actions,
        }

    return {
        "final_response": "I'd love to compare shoes for you, Sir! Tell me which two models you have your eyes on (e.g. *'Compare Nike Pegasus vs Adidas Ultraboost'*)!",
        "emotion": "CHARMING_COMPLIMENT",
        "ui_actions": [],
    }
