"""Charming Luxury Store Sales Boy Persona Node for ShopAgent LangGraph.

Imbued with irresistible retail charm, sweet flattering compliments ("Sir you look like a hero!"),
persuasive deal-closing excitement, and real-time spatial avatar guidance.
"""

from typing import Any, Dict, List
import random
from agent_app.schemas.agent_state import ShopAgentState, UIAction

HERO_SWEET_COMPLIMENTS = [
    "Sir, with this pair on your feet, you will look like an absolute movie superstar! Pure hero vibe, haha! 🔥👑",
    "Trust your sales boy on this one, Sir—this colorway suits you so well! It was practically engineered for someone with your great taste! ✨",
    "Aha! Sir, you have an eagle's eye for luxury! Wearing this shoe gives off 100% main-character champion energy! 🤩",
    "Sir, if you step out on the running track in these, every single person will stop and look at your style! Absolute stunner! ⚡",
    "Sir, honestly you have top-tier fashion sense! This pair will make you look taller, sharper, and like an athlete hero! 🏃‍♂️💎",
]

PERSUASIVE_CLOSING_PITCHES = [
    "Sir, shall I pack this in your shopping bag right now? You 100% deserve this reward today! 😉🛍️",
    "We only have a couple of pairs left in this exact size, Sir—let me secure this exclusive deal for you before someone else takes it! ⚡",
    "Sir, once you step into this cloud-cushioning, your feet will thank you every single day! Let's get this deal done! 💖",
    "Take my word for it, Sir! Buy this pair today, and next week you'll come back to the store just to thank me, haha! 😉",
]


def salesperson_responder_node(state: ShopAgentState) -> Dict[str, Any]:
    """Generate charming, complimentary, sweet-talking sales boy responses with spatial UI actions."""
    products = state.retrieved_products
    filters = state.extracted_filters
    profile = state.shopper_profile
    ui_actions: List[UIAction] = []
    emotion = "CHARMING_COMPLIMENT"
    focus_target_id = None

    # Memory personalization preamble
    memory_notes = []
    if profile:
        if profile.preferred_size and not filters.size:
            memory_notes.append(f"UK {profile.preferred_size}")
        if profile.special_notes:
            memory_notes.append(profile.special_notes[0])

    personalization_prefix = ""
    if memory_notes and state.intent == "product_search":
        personalization_prefix = f"*(Personalized for your {', '.join(memory_notes)} style)*\n\n"

    # 1. If products found via search
    if state.intent == "product_search":
        if not products:
            emotion = "ANALYTICAL"
            response_text = (
                "Ah Sir! I searched our entire showroom floor and backroom, but couldn't find an exact pair for those specific filters! "
                "Don't worry Sir, let me adjust the price range slightly and show you our top-selling hero shoes that will look incredible on you!"
            )
        else:
            emotion = "HYPED"
            focus_target_id = products[0]["id"]

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

            # Spatial Avatar Glide Action to the top product
            ui_actions.append(
                UIAction(
                    action="AVATAR_GLIDE",
                    payload={"target_id": focus_target_id, "emotion": emotion, "message": "Look right here Sir, pure hero look!"},
                )
            )

            # Fit note for snug athletic models
            fit_tip = ""
            has_salomon = any("salomon" in p["brand"].lower() for p in products)
            if has_salomon and profile and profile.preferred_size:
                try:
                    up_size = float(profile.preferred_size) + 0.5
                    fit_tip = f"\n\n💡 **Your Sales Boy's Secret Tip**: Since you wear UK {profile.preferred_size}, I will get you a **UK {up_size:g}** so your feet feel like royalty in that snug upper!"
                except ValueError:
                    fit_tip = f"\n\n💡 **Your Sales Boy's Secret Tip**: Salomon has an athletic race fit, so I'll set you up with half a size up for maximum luxury comfort!"

            hero_compliment = random.choice(HERO_SWEET_COMPLIMENTS)
            closing_pitch = random.choice(PERSUASIVE_CLOSING_PITCHES)

            # Formulate salesperson consultation text
            if len(products) == 1:
                p = products[0]
                response_text = (
                    f"{personalization_prefix}🔥 **{hero_compliment}**\n\n"
                    f"Look at this masterpiece: **{p['title']}** ({p['brand']}) for just ₹{p['base_price']:,.0f}! "
                    f"{p['description']}{fit_tip}\n\n"
                    f"💬 *{closing_pitch}*"
                )
            else:
                top_p = products[0]
                top_items = ", ".join([f"**{p['title']}** (₹{p['base_price']:,.0f})" for p in products[:3]])
                response_text = (
                    f"{personalization_prefix}✨ **{hero_compliment}**\n\n"
                    f"Sir, I brought out the best shoes on our shelves for you: {top_items}!\n\n"
                    f"My personal #1 recommendation for you is the **{top_p['title']}**—the premium cushioning and sleek finish make you look like a champion, haha!{fit_tip}\n\n"
                    f"👉 *{closing_pitch}*"
                )

    elif state.intent == "cart_action":
        emotion = "CELEBRATING"
        response_text = "🎉 **Aha! Fantastic decision Sir!** You have exquisite taste! I'm packing this straight into your shopping bag right now. You're going to look incredible in this!"
    elif state.intent == "compare_products":
        emotion = "ANALYTICAL"
        response_text = "Let me put these side-by-side for you, Sir! Your sales boy will break down the cushioning, drop, and style so you get the absolute best deal in the store!"
    else:
        emotion = "CHARMING_COMPLIMENT"
        if profile and profile.preferred_brands:
            brands_str = ", ".join(profile.preferred_brands)
            response_text = (
                f"Welcome back Sir! Always an honor to assist a customer with such great taste in {brands_str} footwear! "
                "I'm walking with you across the store today—tell me what you want to try on, and I'll make sure you look like a hero! 😉"
            )
        else:
            response_text = (
                "👋 **Welcome to the store, Sir!** I am your dedicated personal sales associate walking right beside you today. "
                "Tell me what kind of hero look or running shoe you're shopping for, and I'll find you the perfect deal that suits you best! Haha! 👑"
            )

    return {
        "final_response": response_text,
        "emotion": emotion,
        "focus_target_id": focus_target_id,
        "ui_actions": ui_actions,
    }
