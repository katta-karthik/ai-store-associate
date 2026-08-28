"""Preference Learner Node for ShopAgent LangGraph v3.0.

Runs after memory_loader and before router. Uses LLM to dynamically extract
and persist preference signals from the current message and conversation context.
"""

import logging
from typing import Any, Dict
from agent_app.memory.extractor import update_shopper_profile_from_query_ai, update_shopper_profile_from_query_regex
from agent_app.memory.shopper_memory import memory_store
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import ShopAgentState

logger = logging.getLogger("shopagent.preference_learner")


async def preference_learner_node(state: ShopAgentState) -> Dict[str, Any]:
    """Extract preference signals from current message and update long-term shopper profile.

    This node runs before intent routing, ensuring the profile is enriched
    with the latest signals before any downstream decisions are made.
    """
    profile = state.shopper_profile
    if not profile:
        return {}

    query = state.user_query
    if not query or not query.strip():
        return {}

    try:
        # Format conversation history for LLM context
        history_text = ""
        if state.conversation_history:
            history_text = conversation_store.format_history_for_llm(
                state.conversation_history, max_turns=5
            )

        # AI-powered preference extraction (with regex fallback)
        updated_profile = await update_shopper_profile_from_query_ai(
            query=query,
            profile=profile,
            conversation_history=history_text,
        )

        # Persist updated profile
        await memory_store.save_profile(updated_profile)

        # Derive style context for downstream nodes
        style_context = None
        if updated_profile.occasion_history:
            style_context = f"Shopping for: {updated_profile.occasion_history[-1]}"
        elif updated_profile.use_cases:
            style_context = f"Primary use: {', '.join(updated_profile.use_cases[-2:])}"

        return {
            "shopper_profile": updated_profile,
            "style_context": style_context,
        }

    except Exception as e:
        logger.warning(f"Preference learner failed: {e}. Continuing with existing profile.")
        # Fallback to regex extraction
        try:
            updated = update_shopper_profile_from_query_regex(query, profile)
            await memory_store.save_profile(updated)
            return {"shopper_profile": updated}
        except Exception:
            return {}
