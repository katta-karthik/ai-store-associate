"""Consultative Salesperson Responder Node for ShopAgent LangGraph."""

from typing import Any, Dict, List
from agent_app.schemas.agent_state import ShopAgentState, UIAction


def salesperson_responder_node(state: ShopAgentState) -> Dict[str, Any]:
    """Generate in-store salesperson conversational response and dispatch UI control actions."""
    products = state.retrieved_products
    filters = state.extracted_filters
    profile = state.shopper_profile
    ui_actions: List[UIAction] = []

    # Memory personalization preamble
    memory_notes = []
    if profile:
        if profile.preferred_size and not filters.size:
            memory_notes.append(f"Size {profile.preferred_size}")
        if profile.special_notes:
            memory_notes.append(profile.special_notes[0])

    personalization_prefix = ""
    if memory_notes and state.intent == "product_search":
        personalization_prefix = f"*(Personalized for your {', '.join(memory_notes)})* "

    # 1. If products found via search
    if state.intent == "product_search":
        if not products:
            response_text = (
                "I looked through our catalog, but couldn't find an exact match for those specific criteria. "
                "Would you like me to broaden the price range or show our top-rated alternatives?"
            )
        else:
            # Build UI action to update browser filters
            filter_payload: Dict[str, Any] = {}
            if filters.category_id:
                filter_payload["category"] = filters.category_id
            if filters.max_price:
                filter_payload["max_price"] = filters.max_price
            if filters.brand:
                filter_payload["brand"] = filters.brand
            if filters.size:
                filter_payload["size"] = filters.size

            if filter_payload:
                ui_actions.append(UIAction(action="SET_FILTERS", payload=filter_payload))

            # Highlight recommended product IDs
            prod_ids = [p["id"] for p in products[:3]]
            ui_actions.append(UIAction(action="HIGHLIGHT_PRODUCTS", payload={"product_ids": prod_ids}))

            # Fit note for snug athletic models
            fit_tip = ""
            has_salomon = any("salomon" in p["brand"].lower() for p in products)
            if has_salomon and profile and profile.preferred_size:
                try:
                    up_size = float(profile.preferred_size) + 0.5
                    fit_tip = f"\n\n💡 **Fit Tip**: Since your profile size is UK {profile.preferred_size}, we recommend sizing up to **UK {up_size:g}** for Salomon footwear."
                except ValueError:
                    fit_tip = f"\n\n💡 **Fit Tip**: Salomon shoes run snug; we recommend half a size up from your normal UK {profile.preferred_size}."

            # Formulate salesperson consultation text
            if len(products) == 1:
                p = products[0]
                response_text = (
                    f"{personalization_prefix}I found the **{p['title']}** ({p['brand']}) for ₹{p['base_price']:,.0f}. "
                    f"{p['description']}{fit_tip}"
                )
            else:
                top_items = ", ".join([f"**{p['title']}** (₹{p['base_price']:,.0f})" for p in products[:3]])
                response_text = (
                    f"{personalization_prefix}I've updated your store filters and found **{len(products)} matching options** for you: {top_items}. "
                    f"Let me know if you want me to compare their cushioning or specs!{fit_tip}"
                )

    elif state.intent == "cart_action":
        response_text = "I can help with your cart! Just tell me which product and size you'd like to add."
    elif state.intent == "compare_products":
        response_text = "I'd be happy to compare those models for you! Which two shoes would you like to evaluate side-by-side?"
    else:
        if profile and profile.preferred_brands:
            brands_str = ", ".join(profile.preferred_brands)
            response_text = (
                f"Welcome back! I'm your AI Store Associate, and I remember you're interested in {brands_str} footwear"
                + (f" in size {profile.preferred_size}" if profile.preferred_size else "")
                + ". What can I help you find today?"
            )
        else:
            response_text = (
                "Hello! I'm your AI Store Associate. I can search our catalog, apply live filters, "
                "compare footwear specs, and manage your cart. What are you shopping for today?"
            )

    return {
        "final_response": response_text,
        "ui_actions": ui_actions,
    }
