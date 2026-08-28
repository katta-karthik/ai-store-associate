"""Shopper Preference Extractor for Long-Term Memory — v3.0 AI-Powered.

Primary: LLM-powered dynamic preference extraction from natural language.
Fallback: Enhanced regex extraction when LLM is unavailable.
"""

import re
import logging
from typing import Any, Dict, List, Optional
from agent_app.memory.shopper_memory import ShopperProfile
from agent_app.core.llm_client import llm_client

logger = logging.getLogger("shopagent.extractor")


async def update_shopper_profile_from_query_ai(
    query: str,
    profile: ShopperProfile,
    conversation_history: str = "",
) -> ShopperProfile:
    """AI-powered preference extraction using Gemini structured output.

    Dynamically learns any brand, style, color, condition, or occasion
    from natural language — not limited to hardcoded lists.
    Falls back to regex extraction if LLM is unavailable.
    """
    if not llm_client.is_available:
        return update_shopper_profile_from_query_regex(query, profile)

    try:
        profile_context = profile.get_personalization_context()
        result = await llm_client.extract_preferences(
            query=query,
            conversation_history=conversation_history,
            current_profile_context=profile_context,
        )

        if not result:
            return update_shopper_profile_from_query_regex(query, profile)

        # Apply positive brand signals
        for brand in result.get("new_brands_liked", []):
            brand_clean = brand.strip().title()
            if brand_clean and brand_clean not in profile.preferred_brands:
                profile.preferred_brands.append(brand_clean)
            # Remove from disliked if they changed their mind
            if brand_clean in profile.disliked_brands:
                profile.disliked_brands.remove(brand_clean)

        # Apply negative brand signals
        for brand in result.get("new_brands_disliked", []):
            brand_clean = brand.strip().title()
            if brand_clean and brand_clean not in profile.disliked_brands:
                profile.disliked_brands.append(brand_clean)
            # Remove from preferred if they changed their mind
            if brand_clean in profile.preferred_brands:
                profile.preferred_brands.remove(brand_clean)

        # Apply style DNA signals
        for style in result.get("new_style_signals", []):
            style_clean = style.strip().lower()
            if style_clean and style_clean not in profile.style_dna:
                profile.style_dna.append(style_clean)

        # Apply color preferences
        for color in result.get("new_color_preferences", []):
            color_clean = color.strip().lower()
            if color_clean and color_clean not in profile.preferred_colors:
                profile.preferred_colors.append(color_clean)

        # Apply foot conditions
        for condition in result.get("new_foot_conditions", []):
            condition_clean = condition.strip().lower()
            if condition_clean and condition_clean not in profile.foot_conditions:
                profile.foot_conditions.append(condition_clean)

        # Apply use cases
        for use_case in result.get("new_use_cases", []):
            uc_clean = use_case.strip().lower()
            if uc_clean and uc_clean not in profile.use_cases:
                profile.use_cases.append(uc_clean)

        # Apply occasions
        for occasion in result.get("new_occasions", []):
            occ_clean = occasion.strip().lower()
            if occ_clean and occ_clean not in profile.occasion_history:
                profile.occasion_history.append(occ_clean)
                # Keep only last 10 occasions
                profile.occasion_history = profile.occasion_history[-10:]

        # Apply budget update
        budget_update = result.get("budget_update")
        if budget_update is not None:
            try:
                profile.budget_max = float(budget_update)
            except (ValueError, TypeError):
                pass

        # Apply size update
        size_update = result.get("size_update")
        if size_update is not None:
            profile.preferred_size = str(size_update).strip()

        # Apply price sensitivity
        price_sensitivity = result.get("price_sensitivity")
        if price_sensitivity and price_sensitivity in ("budget", "mid-range", "premium", "luxury"):
            profile.price_sensitivity = price_sensitivity

        # Apply sentiment
        sentiment = result.get("sentiment")
        if sentiment and sentiment in ("enthusiastic", "cautious", "decisive", "browsing", "frustrated"):
            profile.sentiment_trend = sentiment

        # Apply special notes
        for note in result.get("special_notes", []):
            note_clean = note.strip()
            if note_clean and note_clean not in profile.special_notes:
                profile.special_notes.append(note_clean)
                # Keep only last 10 notes
                profile.special_notes = profile.special_notes[-10:]

        # Increment interaction count
        profile.interaction_count += 1

        return profile

    except Exception as e:
        logger.warning(f"AI preference extraction failed: {e}. Falling back to regex.")
        return update_shopper_profile_from_query_regex(query, profile)


def update_shopper_profile_from_query_regex(query: str, profile: ShopperProfile) -> ShopperProfile:
    """Enhanced regex-based preference extraction (fallback when LLM is unavailable)."""
    q = query.lower()

    # 1. Size extraction (e.g. "I am size 10", "shoe size 9", "uk 10")
    size_match = re.search(r'\b(?:size|uk)\s*(\d{1,2})\b', q)
    if size_match:
        profile.preferred_size = size_match.group(1)

    # 2. Brand preferences — expanded list
    brands = [
        "nike", "adidas", "puma", "salomon", "new balance", "reebok",
        "asics", "brooks", "hoka", "saucony", "under armour", "converse",
        "vans", "jordan", "yeezy", "skechers", "fila",
    ]
    for b in brands:
        if b in q:
            brand_title = b.title()
            # Check for negative signals
            neg_patterns = [f"not {b}", f"no {b}", f"don't like {b}", f"hate {b}", f"dislike {b}", f"except {b}"]
            if any(neg in q for neg in neg_patterns):
                if brand_title not in profile.disliked_brands:
                    profile.disliked_brands.append(brand_title)
                if brand_title in profile.preferred_brands:
                    profile.preferred_brands.remove(brand_title)
            else:
                if brand_title not in profile.preferred_brands:
                    profile.preferred_brands.append(brand_title)

    # 3. Category preferences
    if any(k in q for k in ["road running", "running shoe", "marathon", "5k", "10k"]):
        if "Road Running" not in profile.preferred_categories:
            profile.preferred_categories.append("Road Running")
    if any(k in q for k in ["trail", "hiking", "outdoor", "waterproof", "gore-tex", "gtx"]):
        if "Trail & Outdoor" not in profile.preferred_categories:
            profile.preferred_categories.append("Trail & Outdoor")
    if any(k in q for k in ["sneaker", "casual", "streetwear", "retro", "panda"]):
        if "Lifestyle Sneakers" not in profile.preferred_categories:
            profile.preferred_categories.append("Lifestyle Sneakers")

    # 4. Budget Ceiling
    price_match = re.search(r'(?:under|below|less than|max|budget)\s*(?:₹|rs\.?|inr)?\s*(\d+)(?:k)?', q)
    if price_match:
        val = int(price_match.group(1))
        if "k" in price_match.group(0):
            val *= 1000
        profile.budget_max = float(val)

    # 5. Foot Conditions
    foot_conditions_map = {
        "knee pain": "knee pain",
        "joint pain": "joint pain",
        "wide feet": "wide feet",
        "wide toe box": "wide feet",
        "flat feet": "flat feet",
        "high arch": "high arch",
        "plantar fasciitis": "plantar fasciitis",
        "overpronation": "overpronation",
        "supination": "supination",
    }
    for pattern, condition in foot_conditions_map.items():
        if pattern in q and condition not in profile.foot_conditions:
            profile.foot_conditions.append(condition)

    # 6. Use Cases
    use_case_map = {
        "marathon": "marathon training",
        "long distance": "marathon training",
        "gym": "gym workouts",
        "treadmill": "gym workouts",
        "hiking": "hiking",
        "daily": "daily wear",
        "commute": "daily commute",
        "office": "office wear",
    }
    for pattern, use_case in use_case_map.items():
        if pattern in q and use_case not in profile.use_cases:
            profile.use_cases.append(use_case)

    # 7. Color Preferences
    colors = ["black", "white", "red", "blue", "green", "grey", "gray", "pink", "orange", "yellow", "brown", "navy", "beige"]
    for color in colors:
        if color in q and color not in profile.preferred_colors:
            profile.preferred_colors.append(color)

    # 8. Style DNA
    style_signals = {
        "minimalist": "minimalist",
        "bold": "bold",
        "retro": "retro",
        "classic": "classic",
        "sporty": "sporty",
        "chunky": "chunky",
        "sleek": "sleek",
        "flashy": "flashy",
    }
    for pattern, style in style_signals.items():
        if pattern in q and style not in profile.style_dna:
            profile.style_dna.append(style)

    # 9. Ergonomic & Special Notes (preserved from v2)
    if "knee pain" in q or "joint pain" in q:
        note = "Needs maximum impact cushioning for joint/knee protection"
        if note not in profile.special_notes:
            profile.special_notes.append(note)

    if "wide feet" in q or "wide toe box" in q:
        note = "Prefers wide toe-box fit"
        if note not in profile.special_notes:
            profile.special_notes.append(note)

    if "marathon" in q or "long distance" in q:
        note = "Training for long distance / marathon running"
        if note not in profile.special_notes:
            profile.special_notes.append(note)

    # 10. Increment interaction count
    profile.interaction_count += 1

    return profile


# Legacy sync compatibility wrapper
def update_shopper_profile_from_query(query: str, profile: ShopperProfile) -> ShopperProfile:
    """Synchronous regex-only extraction for backward compatibility."""
    return update_shopper_profile_from_query_regex(query, profile)
