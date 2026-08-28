"""Persistent Conversation History Store for Multi-Turn Context.

Stores per-session conversation turns in SQLite for multi-turn AI personalization.
Enables contextual follow-ups like "something cheaper", "in black", "the first shoe you showed me".
"""

import datetime
import json
import aiosqlite
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class ConversationStore:
    """Async SQLite storage for persistent multi-turn conversation history."""

    MAX_HISTORY_DEPTH = 20  # Maximum messages to retain per session

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = str(backend_dir / "shopper_memory.db")
        else:
            self.db_path = db_path
        self._initialized = False

    async def init_db(self):
        """Create conversation history table if not existing."""
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    shopper_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intent TEXT,
                    product_ids TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_conv_session
                ON conversation_history(session_id, timestamp)
            """)
            await db.commit()
        self._initialized = True

    async def add_message(
        self,
        session_id: str,
        shopper_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist a conversation turn (user or assistant message)."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO conversation_history
                (session_id, shopper_id, role, content, intent, product_ids, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                shopper_id,
                role,
                content,
                intent,
                json.dumps(product_ids or []),
                utc_now_iso(),
                json.dumps(metadata or {}),
            ))
            await db.commit()

        # Enforce max history depth — prune oldest messages
        await self._prune_old_messages(session_id)

    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session, ordered chronologically."""
        await self.init_db()
        max_msgs = limit or self.MAX_HISTORY_DEPTH

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT role, content, intent, product_ids, timestamp, metadata
                FROM conversation_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, max_msgs))
            rows = await cursor.fetchall()

        # Reverse to get chronological order
        messages = []
        for row in reversed(rows):
            row_dict = dict(row)
            try:
                row_dict["product_ids"] = json.loads(row_dict.get("product_ids") or "[]")
            except (json.JSONDecodeError, TypeError):
                row_dict["product_ids"] = []
            try:
                row_dict["metadata"] = json.loads(row_dict.get("metadata") or "{}")
            except (json.JSONDecodeError, TypeError):
                row_dict["metadata"] = {}
            messages.append(row_dict)

        return messages

    def format_history_for_llm(
        self,
        history: List[Dict[str, Any]],
        max_turns: int = 10,
    ) -> str:
        """Format conversation history into a concise string for LLM context injection.

        Produces a compact transcript like:
            Customer: "Show me Nike running shoes under 8000"
            Associate: "Here are 3 Nike running shoes..." [showed: Pegasus 41, Air Zoom]
            Customer: "Something cheaper?"
        """
        if not history:
            return ""

        recent = history[-max_turns * 2:]  # Each turn = user + assistant
        lines = []
        for msg in recent:
            role_label = "Customer" if msg["role"] == "user" else "Associate"
            content = msg["content"]
            # Truncate long assistant responses for token efficiency
            if msg["role"] == "assistant" and len(content) > 200:
                content = content[:200] + "..."
            product_note = ""
            pids = msg.get("product_ids", [])
            if pids and msg["role"] == "assistant":
                product_note = f" [showed {len(pids)} products]"
            lines.append(f'{role_label}: "{content}"{product_note}')

        return "\n".join(lines)

    async def get_last_shown_products(self, session_id: str) -> List[str]:
        """Get product IDs from the most recent assistant response for follow-up context."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT product_ids FROM conversation_history
                WHERE session_id = ? AND role = 'assistant' AND product_ids != '[]'
                ORDER BY timestamp DESC LIMIT 1
            """, (session_id,))
            row = await cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    return []
        return []

    async def _prune_old_messages(self, session_id: str) -> None:
        """Keep only the most recent MAX_HISTORY_DEPTH messages per session."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM conversation_history
                WHERE session_id = ? AND id NOT IN (
                    SELECT id FROM conversation_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """, (session_id, session_id, self.MAX_HISTORY_DEPTH))
            await db.commit()

    async def clear_history(self, session_id: str) -> None:
        """Clear conversation history for a session (GDPR/privacy)."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM conversation_history WHERE session_id = ?",
                (session_id,)
            )
            await db.commit()


conversation_store = ConversationStore()
