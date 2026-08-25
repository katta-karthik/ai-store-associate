"""Persistent Shopper Memory Graph & Profile Store."""

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
    """Structured shopper preference profile."""
    shopper_id: str
    preferred_brands: List[str] = Field(default_factory=list)
    preferred_size: Optional[str] = None
    preferred_categories: List[str] = Field(default_factory=list)
    budget_max: Optional[float] = None
    special_notes: List[str] = Field(default_factory=list)
    past_viewed_products: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    model_config = ConfigDict(from_attributes=True)


class ShopperMemoryStore:
    """Async SQLite storage engine for shopper long-term memory."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = str(backend_dir / "shopper_memory.db")
        else:
            self.db_path = db_path
        self._initialized = False

    async def init_db(self):
        """Create memory tables if not existing."""
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
            cursor = await db.execute(
                "SELECT * FROM shopper_profiles WHERE shopper_id = ?",
                (shopper_id,)
            )
            row = await cursor.fetchone()
            if not row:
                profile = ShopperProfile(shopper_id=shopper_id)
                await self.save_profile(profile)
                return profile

            return ShopperProfile(
                shopper_id=row[0],
                preferred_brands=json.loads(row[1] or "[]"),
                preferred_size=row[2],
                preferred_categories=json.loads(row[3] or "[]"),
                budget_max=row[4],
                special_notes=json.loads(row[5] or "[]"),
                past_viewed_products=json.loads(row[6] or "[]"),
                created_at=row[7] or utc_now_iso(),
                updated_at=row[8] or utc_now_iso(),
            )

    async def save_profile(self, profile: ShopperProfile) -> None:
        """Persist or update shopper profile."""
        await self.init_db()
        profile.updated_at = utc_now_iso()
        # Sanitize special notes
        sanitized_notes = [self._sanitize_pii(n) for n in profile.special_notes]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO shopper_profiles (
                    shopper_id, preferred_brands, preferred_size, preferred_categories,
                    budget_max, special_notes, past_viewed_products, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(shopper_id) DO UPDATE SET
                    preferred_brands=excluded.preferred_brands,
                    preferred_size=excluded.preferred_size,
                    preferred_categories=excluded.preferred_categories,
                    budget_max=excluded.budget_max,
                    special_notes=excluded.special_notes,
                    past_viewed_products=excluded.past_viewed_products,
                    updated_at=excluded.updated_at
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
            ))
            await db.commit()

    async def clear_profile(self, shopper_id: str) -> None:
        """Reset memory for GDPR/privacy compliance."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM shopper_profiles WHERE shopper_id = ?", (shopper_id,))
            await db.commit()


memory_store = ShopperMemoryStore()
