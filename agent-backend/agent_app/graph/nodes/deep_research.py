"""Multi-Constraint Deep Shopping Research & Recursive Sub-Agent Council Node v3.1 (Prime Agent RLM Architecture).

Executes parallel isolated sub-agents:
1. Biomechanics & Ergonomics Specialist Sub-Agent
2. Value & Pricing Optimization Sub-Agent
3. Style DNA & Aesthetic Critic Sub-Agent
Then recursively synthesizes their findings into an authoritative salesperson recommendation.
"""

import logging
from typing import Any, Dict, List, Optional
from agent_app.core.llm_client import llm_client
from agent_app.core.recursive_runner import SubAgentTask, recursive_runner
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState, UIAction
from agent_app.tools.store_tools import store_client

logger = logging.getLogger("shopagent.deep_research")


def _score_product_fit(product: Dict[str, Any], query: str, profile_notes: List[str]) -> Dict[str, Any]:
    """Score a product against complex constraints and compute fit confidence (rule fallback)."""
    score = 78
    pros = []
    tradeoffs = []
    badges = []

    title = product.get("title", "").lower()
    desc = product.get("description", "").lower()
    brand = product.get("brand", "").lower()
    price = product.get("base_price", 0)

    # 1. Biomechanics / Cushioning
    if any(k in query for k in ["flat feet", "overpronation", "knee pain", "cushion", "joint", "plantar"]):
        if "zoom" in desc or "boost" in desc or "air" in desc or "cushion" in desc or "react" in desc:
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
    """Execute multi-phase deep research analysis powered by recursive sub-agents."""
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

    # 🌲 Spawn Recursive Sub-Agent Council for Top Match (Prime Agent Architecture)
    council_tasks = [
        SubAgentTask(
            subagent_id=f"subagent_biomech_{top_p['id']}",
            role_name="🔬 Biomechanics & Ergonomics Specialist",
            specialty="Biomechanics, impact dispersion, gait stability, and joint cushioning",
            objective="Evaluate the midsole cushioning, arch support, and joint protection for the shopper.",
            context_slice={"product": top_p, "query": state.user_query, "profile_notes": profile_notes},
        ),
        SubAgentTask(
            subagent_id=f"subagent_value_{top_p['id']}",
            role_name="💰 Value & Pricing Strategist",
            specialty="Cost-per-mile efficiency, build durability, and luxury ROI",
            objective="Evaluate whether the price point matches build quality and durability expectations.",
            context_slice={"product": top_p, "query": state.user_query, "profile_notes": profile_notes},
        ),
        SubAgentTask(
            subagent_id=f"subagent_style_{top_p['id']}",
            role_name="🎨 Style DNA & Aesthetic Critic",
            specialty="Silhouette design, streetwear versatility, and colorway coordination",
            objective="Assess aesthetic alignment with modern street and athletic styling.",
            context_slice={"product": top_p, "query": state.user_query, "profile_notes": profile_notes},
        ),
    ]

    # Execute council in parallel
    council_results = await recursive_runner.execute_parallel_council(council_tasks)

    # Recursively synthesize results
    profile_summary = profile.get_personalization_context() if profile else ""
    synthesized_pitch = await recursive_runner.recursive_synthesize(
        headline_goal=state.user_query,
        council_results=council_results,
        shopper_profile_summary=profile_summary,
    )

    # Top eval augmented with council badges
    all_council_badges = []
    for r in council_results:
        all_council_badges.extend(r.badges)
    if all_council_badges:
        top_eval["badges"] = list(set(top_eval.get("badges", []) + all_council_badges))

    highlight_ids = [c[0]["id"] for c in top_candidates]
    ui_actions = [
        UIAction(action="HIGHLIGHT_PRODUCTS", payload={"product_ids": highlight_ids}),
        UIAction(
            action="SHOW_RESEARCH_REPORT",
            payload={
                "top_product": top_eval,
                "runner_up": runner_eval,
                "all_evals": [c[1] for c in top_candidates],
                "subagent_council": [r.model_dump() for r in council_results],
            },
        ),
        UIAction(
            action="AVATAR_GLIDE",
            payload={"target_id": top_p["id"], "emotion": "HYPED", "message": "Certified by our AI Specialist Council, Sir!"},
        ),
    ]

    return {
        "final_response": synthesized_pitch,
        "emotion": "HYPED",
        "focus_target_id": top_p["id"],
        "ui_actions": ui_actions,
        "retrieved_products": [c[0] for c in top_candidates],
        "metadata": {
            "subagent_council_count": len(council_results),
            "council_avg_confidence": sum(r.confidence_score for r in council_results) // len(council_results),
        },
    }
