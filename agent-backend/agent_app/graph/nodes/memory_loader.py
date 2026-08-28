"""Memory Loader & Synchronizer Node for ShopAgent LangGraph v3.0."""

from typing import Any, Dict
from agent_app.memory.conversation_store import conversation_store
from agent_app.memory.shopper_memory import memory_store
from agent_app.schemas.agent_state import ShopAgentState


async def memory_loader_node(state: ShopAgentState) -> Dict[str, Any]:
    """Retrieve long-term shopper profile and multi-turn conversation history."""
    shopper_id = state.shopper_id or "shopper_default"
    session_id = state.session_id or "default_session"

    # 1. Fetch Shopper Profile
    profile = await memory_store.get_profile(shopper_id)

    # 2. Fetch Conversation History if not already provided in state
    history = state.conversation_history
    if not history:
        history = await conversation_store.get_history(session_id, limit=20)

    return {
        "shopper_profile": profile,
        "conversation_history": history,
    }
