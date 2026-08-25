"""Memory Loader & Synchronizer Node for ShopAgent LangGraph."""

from typing import Any, Dict
from agent_app.memory.extractor import update_shopper_profile_from_query
from agent_app.memory.shopper_memory import memory_store
from agent_app.schemas.agent_state import ShopAgentState


async def memory_loader_node(state: ShopAgentState) -> Dict[str, Any]:
    """Retrieve long-term memory, extract new preference signals, and persist updates."""
    shopper_id = state.shopper_id or state.session_id or "shopper_default"

    # 1. Fetch Profile
    profile = await memory_store.get_profile(shopper_id)

    # 2. Extract signals from current query
    if state.user_query:
        profile = update_shopper_profile_from_query(state.user_query, profile)
        await memory_store.save_profile(profile)

    return {"shopper_profile": profile}
