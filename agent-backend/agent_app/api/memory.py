"""Shopper Memory & Profile API Router."""

from fastapi import APIRouter
from agent_app.memory.shopper_memory import ShopperProfile, memory_store

router = APIRouter(prefix="/shopper", tags=["Shopper Memory"])


@router.get("/{shopper_id}/memory", response_model=ShopperProfile)
async def get_shopper_memory(shopper_id: str):
    """Retrieve long-term memory and preferences for a shopper."""
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
