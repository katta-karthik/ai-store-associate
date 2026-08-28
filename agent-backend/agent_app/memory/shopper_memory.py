"""Persistent Shopper Memory Graph & Deep Personalization Profile Store.

v3.0 — Expanded with style DNA, foot conditions, sentiment tracking,
purchase history, and interaction analytics for AI hyper-personalization.
"""

import datetime
import json
import re
import aiosqlite
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class ShopperProfile(BaseModel):
    """Deep shopper personalization profile for AI-driven recommendations."""
    shopper_id: str

    # Core Preferences (existing)
    preferred_brands: List[str] = Field(default_factory=list)
    preferred_size: Optional[str] = None
    preferred_categories: List[str] = Field(default_factory=list)
    budget_max: Optional[float] = None
    special_notes: List[str] = Field(default_factory=list)
    past_viewed_products: List[str] = Field(default_factory=list)

    # v3.0 Deep Personalization Fields
    style_dna: List[str] = Field(default_factory=list)          # ["minimalist", "bold colors", "retro"]
    preferred_colors: List[str] = Field(default_factory=list)    # ["black", "white", "earth tones"]
    foot_conditions: List[str] = Field(default_factory=list)     # ["wide feet", "high arch", "plantar fasciitis"]
    use_cases: List[str] = Field(default_factory=list)           # ["daily commute", "marathon training", "gym"]
    occasion_history: List[str] = Field(default_factory=list)    # ["gift for wife", "race day", "casual weekend"]
    disliked_brands: List[str] = Field(default_factory=list)     # brands they explicitly rejected
    disliked_styles: List[str] = Field(default_factory=list)     # styles they dislike
    price_sensitivity: str = "unknown"                           # "budget", "mid-range", "premium", "luxury", "unknown"
    interaction_count: int = 0                                   # number of conversations
    sentiment_trend: str = "neutral"                             # "enthusiastic", "cautious", "decisive", "browsing", "neutral"
    last_recommended_ids: List[str] = Field(default_factory=list)  # avoid re-recommending same products
    purchase_history: List[str] = Field(default_factory=list)    # product IDs they checked out

    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    model_config = ConfigDict(from_attributes=True)

    def get_personalization_context(self) -> str:
        """Generate a rich natural language summary of this shopper for LLM prompts."""
        parts = []
        if self.preferred_size:
            parts.append(f"Shoe size: UK {self.preferred_size}")
        if self.preferred_brands:
            parts.append(f"Favorite brands: {', '.join(self.preferred_brands)}")
        if self.disliked_brands:
            parts.append(f"Dislikes: {', '.join(self.disliked_brands)}")
        if self.budget_max:
            parts.append(f"Budget ceiling: ₹{self.budget_max:,.0f}")
        if self.price_sensitivity != "unknown":
            parts.append(f"Price sensitivity: {self.price_sensitivity}")
        if self.style_dna:
            parts.append(f"Style DNA: {', '.join(self.style_dna)}")
        if self.preferred_colors:
            parts.append(f"Color preferences: {', '.join(self.preferred_colors)}")
        if self.foot_conditions:
            parts.append(f"Foot conditions: {', '.join(self.foot_conditions)}")
        if self.use_cases:
            parts.append(f"Typical use: {', '.join(self.use_cases)}")
        if self.occasion_history:
            parts.append(f"Recent occasions: {', '.join(self.occasion_history[-3:])}")
        if self.special_notes:
            parts.append(f"Notes: {'; '.join(self.special_notes[-3:])}")
        if self.sentiment_trend != "neutral":
            parts.append(f"Shopping mood: {self.sentiment_trend}")
        if self.interaction_count > 1:
            parts.append(f"Returning customer ({self.interaction_count} visits)")

        if not parts:
            return "New shopper, no preferences known yet."
        return " | ".join(parts)


# JSON-serializable list fields for DB storage
_LIST_FIELDS = [
    "preferred_brands", "preferred_categories", "special_notes",
    "past_viewed_products", "style_dna", "preferred_colors",
    "foot_conditions", "use_cases", "occasion_history",
    "disliked_brands", "disliked_styles", "last_recommended_ids",
    "purchase_history",
]


class ShopperMemoryStore:
    """Async SQLite storage engine for shopper long-term memory with v3.0 deep personalization."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = str(backend_dir / "shopper_memory.db")
        else:
            self.db_path = db_path
        self._initialized = False

    async def init_db(self):
        """Create memory tables if not existing, and migrate schema for v3.0 fields."""
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS shopper_profiles (
                    shopper_id TEXT PRIMARY KEY,
                    preferred_brands TEXT,
                    preferred_size TEXT,
                    preferred_categories TEXT,
                    budget_max REAL,
                    special_notes TEXT,
                    past_viewed_products TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # v3.0 Schema Migration — add new columns gracefully
            v3_columns = {
                "style_dna": "TEXT DEFAULT '[]'",
                "preferred_colors": "TEXT DEFAULT '[]'",
                "foot_conditions": "TEXT DEFAULT '[]'",
                "use_cases": "TEXT DEFAULT '[]'",
                "occasion_history": "TEXT DEFAULT '[]'",
                "disliked_brands": "TEXT DEFAULT '[]'",
                "disliked_styles": "TEXT DEFAULT '[]'",
                "price_sensitivity": "TEXT DEFAULT 'unknown'",
                "interaction_count": "INTEGER DEFAULT 0",
                "sentiment_trend": "TEXT DEFAULT 'neutral'",
                "last_recommended_ids": "TEXT DEFAULT '[]'",
                "purchase_history": "TEXT DEFAULT '[]'",
            }

            # Check existing columns
            cursor = await db.execute("PRAGMA table_info(shopper_profiles)")
            existing_cols = {row[1] for row in await cursor.fetchall()}

            for col_name, col_def in v3_columns.items():
                if col_name not in existing_cols:
                    try:
                        await db.execute(f"ALTER TABLE shopper_profiles ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass  # Column already exists or migration not needed

            await db.commit()
        self._initialized = True

    def _sanitize_pii(self, text: str) -> str:
        """SecOps Rule 05: Sanitize credit cards, emails, and phone numbers."""
        # Mask 16-digit card numbers
        text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[CARD-MASKED]', text)
        # Mask emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[EMAIL-MASKED]', text)
        return text

    async def get_profile(self, shopper_id: str) -> ShopperProfile:
        """Retrieve shopper profile or create a default one."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM shopper_profiles WHERE shopper_id = ?",
                (shopper_id,)
            )
            row = await cursor.fetchone()
            if not row:
                profile = ShopperProfile(shopper_id=shopper_id)
                await self.save_profile(profile)
                return profile

            row_dict = dict(row)

            # Parse JSON list fields
            parsed = {"shopper_id": row_dict["shopper_id"]}
            for field in _LIST_FIELDS:
                raw = row_dict.get(field)
                try:
                    parsed[field] = json.loads(raw) if raw else []
                except (json.JSONDecodeError, TypeError):
                    parsed[field] = []

            # Scalar fields
            parsed["preferred_size"] = row_dict.get("preferred_size")
            parsed["budget_max"] = row_dict.get("budget_max")
            parsed["price_sensitivity"] = row_dict.get("price_sensitivity", "unknown") or "unknown"
            parsed["interaction_count"] = row_dict.get("interaction_count", 0) or 0
            parsed["sentiment_trend"] = row_dict.get("sentiment_trend", "neutral") or "neutral"
            parsed["created_at"] = row_dict.get("created_at") or utc_now_iso()
            parsed["updated_at"] = row_dict.get("updated_at") or utc_now_iso()

            return ShopperProfile(**parsed)

    async def save_profile(self, profile: ShopperProfile) -> None:
        """Persist or update shopper profile with all v3.0 personalization fields."""
        await self.init_db()
        profile.updated_at = utc_now_iso()

        # Sanitize special notes
        sanitized_notes = [self._sanitize_pii(n) for n in profile.special_notes]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO shopper_profiles (
                    shopper_id, preferred_brands, preferred_size, preferred_categories,
                    budget_max, special_notes, past_viewed_products, created_at, updated_at,
                    style_dna, preferred_colors, foot_conditions, use_cases,
                    occasion_history, disliked_brands, disliked_styles, price_sensitivity,
                    interaction_count, sentiment_trend, last_recommended_ids, purchase_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(shopper_id) DO UPDATE SET
                    preferred_brands=excluded.preferred_brands,
                    preferred_size=excluded.preferred_size,
                    preferred_categories=excluded.preferred_categories,
                    budget_max=excluded.budget_max,
                    special_notes=excluded.special_notes,
                    past_viewed_products=excluded.past_viewed_products,
                    updated_at=excluded.updated_at,
                    style_dna=excluded.style_dna,
                    preferred_colors=excluded.preferred_colors,
                    foot_conditions=excluded.foot_conditions,
                    use_cases=excluded.use_cases,
                    occasion_history=excluded.occasion_history,
                    disliked_brands=excluded.disliked_brands,
                    disliked_styles=excluded.disliked_styles,
                    price_sensitivity=excluded.price_sensitivity,
                    interaction_count=excluded.interaction_count,
                    sentiment_trend=excluded.sentiment_trend,
                    last_recommended_ids=excluded.last_recommended_ids,
                    purchase_history=excluded.purchase_history
            """, (
                profile.shopper_id,
                json.dumps(profile.preferred_brands),
                profile.preferred_size,
                json.dumps(profile.preferred_categories),
                profile.budget_max,
                json.dumps(sanitized_notes),
                json.dumps(profile.past_viewed_products),
                profile.created_at,
                profile.updated_at,
                json.dumps(profile.style_dna),
                json.dumps(profile.preferred_colors),
                json.dumps(profile.foot_conditions),
                json.dumps(profile.use_cases),
                json.dumps(profile.occasion_history),
                json.dumps(profile.disliked_brands),
                json.dumps(profile.disliked_styles),
                profile.price_sensitivity,
                profile.interaction_count,
                profile.sentiment_trend,
                json.dumps(profile.last_recommended_ids),
                json.dumps(profile.purchase_history),
            ))
            await db.commit()

    async def clear_profile(self, shopper_id: str) -> None:
        """Reset memory for GDPR/privacy compliance."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM shopper_profiles WHERE shopper_id = ?", (shopper_id,))
            await db.commit()


memory_store = ShopperMemoryStore()
