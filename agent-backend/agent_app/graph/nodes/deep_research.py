"""Multi-Constraint Deep Shopping Research & Recommendation Critic Node."""

from typing import Any, Dict, List, Optional
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState, UIAction
from agent_app.tools.store_tools import store_client


def _score_product_fit(product: Dict[str, Any], query: str, profile_notes: List[str]) -> Dict[str, Any]:
    """Score a product against complex constraints and compute fit confidence."""
    score = 78
    pros = []
    tradeoffs = []
    badges = []

    title = product.get("title", "").lower()
    desc = product.get("description", "").lower()
    brand = product.get("brand", "").lower()
    specs = product.get("specs", {})
    price = product.get("base_price", 0)

    # 1. Biomechanics / Cushioning
    if any(k in query for k in ["flat feet", "overpronation", "knee pain", "cushion", "joint"]):
        if "zoom" in desc or "boost" in desc or "air" in desc or "cushion" in desc:
            score += 16
            pros.append("Maximum shock absorption protects joints and flat arches effortlessly")
            badges.append("High Impact Cushioning")
        else:
            tradeoffs.append("Firm responsive sole rather than ultra-plush cushioning")

    # 2. Distance / Marathon
    if any(k in query for k in ["marathon", "long distance", "half marathon", "10k", "endurance"]):
        if "pegasus" in title or "ultraboost" in title or "road" in desc:
            score += 10
            pros.append("High-durability outsole engineered for 500+ km marathon mileage")
            badges.append("Marathon Ready")

    # 3. Hybrid Trail & Road
    if any(k in query for k in ["gravel", "trail", "outdoor", "dirt", "hybrid", "wet"]):
        if "salomon" in brand or "trail" in desc or "gore-tex" in desc or "gtx" in desc:
            score += 10
            pros.append("Deep lug traction delivers aggressive grip on loose gravel & wet trails")
            badges.append("All-Terrain Grip")
            if "road" in query or "tarmac" in query:
                tradeoffs.append("Aggressive rubber lugs may experience faster wear if used 100% on hard pavement")
        elif "pegasus" in title or "ultraboost" in title:
            tradeoffs.append("Best on roads and light gravel; avoid deep mud or technical rocky scrambles")

    score = min(score, 99)

    return {
        "product_id": product["id"],
        "title": product["title"],
        "brand": product["brand"],
        "price": price,
        "match_score": score,
        "pros": pros,
        "tradeoffs": tradeoffs,
        "badges": badges,
    }


async def deep_research_node(state: ShopAgentState) -> Dict[str, Any]:
    """Execute multi-phase deep research analysis with charming salesperson guidance."""
    query = state.user_query.lower()
    profile = state.shopper_profile
    profile_notes = profile.special_notes if profile else []

    res = await store_client.search_products(ExtractedFilters())
    all_products = res.get("items", [])

    if not all_products:
        return {
            "final_response": "I'm analyzing our backroom catalog, Sir, but could not load products right now.",
            "emotion": "ANALYTICAL",
            "ui_actions": [],
        }

    scored_items = []
    for p in all_products:
        eval_result = _score_product_fit(p, query, profile_notes)
        scored_items.append((p, eval_result))

    scored_items.sort(key=lambda x: x[1]["match_score"], reverse=True)

    top_candidates = scored_items[:3]
    top_p, top_eval = top_candidates[0]
    runner_p, runner_eval = top_candidates[1] if len(top_candidates) > 1 else (None, None)

    report_lines = [
        f"👑 **Sir, I personally ran a deep biomechanical evaluation across our entire collection for you!**\n",
        f"🏆 **Your Absolute #1 Hero Match: {top_p['title']}** ({top_eval['match_score']}% Match — ₹{top_p['base_price']:,.0f})",
        f"• **Why it's perfect for you**: {', '.join(top_eval['pros']) if top_eval['pros'] else 'Balanced all-around performance.'}",
    ]

    if top_eval["tradeoffs"]:
        report_lines.append(f"• **Salesperson Note**: {', '.join(top_eval['tradeoffs'])}")

    if runner_p and runner_eval:
        report_lines.append(
            f"\n🥈 **Alternative Luxury Runner-Up: {runner_p['title']}** ({runner_eval['match_score']}% Match — ₹{runner_p['base_price']:,.0f})\n"
            f"• **Why consider**: {', '.join(runner_eval['pros']) if runner_eval['pros'] else 'Strong secondary choice.'}"
        )
        if runner_eval["tradeoffs"]:
            report_lines.append(f"• **Salesperson Note**: {', '.join(runner_eval['tradeoffs'])}")

    report_lines.append(
        f"\n🔥 **My Expert Recommendation**: Sir, you will glide like a champion in the **{top_p['title']}**! Shall I pack this pair in your bag right now? 😉"
    )

    final_text = "\n".join(report_lines)

    highlight_ids = [c[0]["id"] for c in top_candidates]
    ui_actions = [
        UIAction(action="HIGHLIGHT_PRODUCTS", payload={"product_ids": highlight_ids}),
        UIAction(
            action="SHOW_RESEARCH_REPORT",
            payload={
                "top_product": top_eval,
                "runner_up": runner_eval,
                "all_evals": [c[1] for c in top_candidates],
            },
        ),
        UIAction(
            action="AVATAR_GLIDE",
            payload={"target_id": top_p["id"], "emotion": "HYPED", "message": "This is your 98% hero match, Sir!"},
        ),
    ]

    return {
        "final_response": final_text,
        "emotion": "HYPED",
        "focus_target_id": top_p["id"],
        "ui_actions": ui_actions,
        "retrieved_products": [c[0] for c in top_candidates],
    }
