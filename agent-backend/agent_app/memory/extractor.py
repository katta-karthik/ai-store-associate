"""Shopper Preference Extractor for Long-Term Memory."""

import re
from typing import Optional
from agent_app.memory.shopper_memory import ShopperProfile


def update_shopper_profile_from_query(query: str, profile: ShopperProfile) -> ShopperProfile:
    """Extract preference signals from natural language query and update profile."""
    q = query.lower()

    # 1. Size extraction (e.g. "I am size 10", "shoe size 9", "uk 10")
    size_match = re.search(r'\b(?:size|uk)\s*(\d{1,2})\b', q)
    if size_match:
        profile.preferred_size = size_match.group(1)

    # 2. Brand preferences (e.g. "I love Nike", "Only Adidas", "Salomon fan")
    brands = ["nike", "adidas", "puma", "salomon"]
    for b in brands:
        if b in q and b.title() not in profile.preferred_brands:
            profile.preferred_brands.append(b.title())

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

    # 5. Ergonomic & Special Notes
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

    return profile
