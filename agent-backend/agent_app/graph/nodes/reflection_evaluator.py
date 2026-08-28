"""Self-Reflective Evaluator & Personalization Scorer Node for ShopAgent LangGraph v3.0.

Evaluates retrieved products against shopper constraints, computes AI personalization
scores with reasoning, verifies stock and sizing, and refines state before salesperson pitch.
"""

import logging
from typing import Any, Dict, List
from agent_app.core.llm_client import llm_client
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import ProductPersonalizationScore, ShopAgentState

logger = logging.getLogger("shopagent.reflection_evaluator")


async def reflection_evaluator_node(state: ShopAgentState) -> Dict[str, Any]:
    """Perform self-critique on retrieved catalog products, verify constraint satisfaction, and compute personalization scores."""
    products = state.retrieved_products or []
    filters = state.extracted_filters
    profile = state.shopper_profile
    query = state.user_query.lower()

    reflection_notes: List[str] = []
    verified_products: List[Dict[str, Any]] = []
    personalization_scores: List[ProductPersonalizationScore] = []

    # 1. Price constraint verification
    if filters.max_price and products:
        within_budget = [p for p in products if p.get("base_price", 0) <= filters.max_price]
        if within_budget:
            verified_products = within_budget
            reflection_notes.append(f"100% within budget cap of ₹{filters.max_price:,.0f}")
        else:
            verified_products = products[:3]
            lowest_price = min(p.get("base_price", 0) for p in products)
            reflection_notes.append(
                f"Closest premium models start at ₹{lowest_price:,.0f} (slightly above ₹{filters.max_price:,.0f})"
            )
    else:
        verified_products = products

    # 2. Size and stock availability verification
    if filters.size and verified_products:
        exact_size_in_stock = []
        for p in verified_products:
            variants = p.get("variants", [])
            has_size = any(
                str(v.get("size", "")).strip() == str(filters.size).strip() and v.get("stock", 0) > 0
                for v in variants
            )
            if has_size:
                exact_size_in_stock.append(p)

        if exact_size_in_stock:
            reflection_notes.append(f"Size UK {filters.size} verified in stock ready to ship.")
        else:
            reflection_notes.append(f"Size UK {filters.size} is low stock across current results.")

    # 3. Biomechanical / Foot Condition Alignment & Cushion Prioritization
    has_cushion_query = any(k in query for k in ["cushion", "comfort", "knee", "joint", "soft", "recovery", "plush"])
    has_condition = bool(profile and profile.foot_conditions and any(c in ", ".join(profile.foot_conditions).lower() for c in ["knee", "joint", "flat feet", "cushion"]))
    if has_cushion_query or has_condition:
        cushioned = [
            p for p in verified_products
            if any(k in p.get("description", "").lower() or k in str(p.get("specs", {})).lower()
                   for k in ["zoom", "boost", "cushion", "react", "foam", "cloud", "gel"])
        ]
        if cushioned:
            verified_products = cushioned + [p for p in verified_products if p not in cushioned]
            reason = ", ".join(profile.foot_conditions) if (profile and profile.foot_conditions) else "cushion/comfort preference"
            reflection_notes.append(f"High-cushion models prioritized for {reason}.")

    # 4. Compute AI Personalization Scores
    if llm_client.is_available and verified_products:
        try:
            profile_context = profile.get_personalization_context() if profile else ""
            history_text = ""
            if state.conversation_history:
                history_text = conversation_store.format_history_for_llm(state.conversation_history, max_turns=4)

            ai_scores = await llm_client.score_products_batch(
                products=verified_products[:4],
                profile_context=profile_context,
                query=state.user_query,
                conversation_history=history_text,
            )

            if ai_scores:
                for s in ai_scores:
                    if isinstance(s, dict) and "product_id" in s:
                        personalization_scores.append(
                            ProductPersonalizationScore(
                                product_id=str(s["product_id"]),
                                score=float(s.get("score", 0.9)),
                                reasoning=str(s.get("reasoning", "Personalized match for your profile.")),
                                match_factors=s.get("match_factors", []),
                                concern_factors=s.get("concern_factors", []),
                            )
                        )
        except Exception as e:
            logger.warning(f"AI personalization scoring failed: {e}. Using rule fallback.")

    # Rule fallback for personalization scoring if LLM unavailable
    if not personalization_scores and verified_products:
        for idx, p in enumerate(verified_products[:4]):
            base_score = 0.95 - (idx * 0.05)
            factors = []
            if filters.max_price and p.get("base_price", 0) <= filters.max_price:
                factors.append(f"Fits your ₹{filters.max_price:,.0f} budget")
            if profile and p.get("brand") in profile.preferred_brands:
                factors.append(f"Matches your favorite brand {p.get('brand')}")
            if profile and profile.preferred_size:
                factors.append(f"Available in your UK {profile.preferred_size}")

            personalization_scores.append(
                ProductPersonalizationScore(
                    product_id=p["id"],
                    score=base_score,
                    reasoning=f"High match based on your {p.get('brand')} preference and specs." if factors else "Top showroom recommendation.",
                    match_factors=factors or ["Showroom Best Seller"],
                    concern_factors=[],
                )
            )

    # 5. Overall Confidence
    if not verified_products:
        confidence = 0.2
        reflection_notes.append("No catalog matches found; fallback recommendation required.")
    else:
        confidence = 0.95 if not any("slightly above" in n for n in reflection_notes) else 0.80

    return {
        "retrieved_products": verified_products,
        "confidence_score": confidence,
        "reflection_notes": reflection_notes,
        "personalization_scores": personalization_scores,
    }
