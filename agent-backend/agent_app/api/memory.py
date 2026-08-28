"""Shopper Memory & Profile API Router v3.0."""

from typing import Any, Dict, List
from fastapi import APIRouter
from agent_app.memory.conversation_store import conversation_store
from agent_app.memory.shopper_memory import ShopperProfile, memory_store

router = APIRouter(prefix="/shopper", tags=["Shopper Memory"])


@router.get("/{shopper_id}/memory", response_model=ShopperProfile)
async def get_shopper_memory(shopper_id: str):
    """Retrieve long-term memory and deep preferences for a shopper."""
    return await memory_store.get_profile(shopper_id)


@router.post("/{shopper_id}/memory", response_model=ShopperProfile)
async def update_shopper_memory(shopper_id: str, profile: ShopperProfile):
    """Manually update or override shopper preferences."""
    profile.shopper_id = shopper_id
    await memory_store.save_profile(profile)
    return profile


@router.delete("/{shopper_id}/memory")
async def clear_shopper_memory(shopper_id: str):
    """Clear memory for privacy/GDPR compliance."""
    await memory_store.clear_profile(shopper_id)
    return {"success": True, "message": f"Memory for shopper {shopper_id} cleared"}


@router.get("/session/{session_id}/history")
async def get_session_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve multi-turn conversation history for a session."""
    return await conversation_store.get_history(session_id)


@router.delete("/session/{session_id}/history")
async def clear_session_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    await conversation_store.clear_history(session_id)
    return {"success": True, "message": f"History for session {session_id} cleared"}
