"""Cart & Wishlist Manager Node for ShopAgent LangGraph."""

import re
from typing import Any, Dict
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState, UIAction
from agent_app.tools.store_tools import store_client


async def cart_manager_node(state: ShopAgentState) -> Dict[str, Any]:
    """Execute cart or wishlist mutation and format salesperson confirmation."""
    query = state.user_query.lower().strip()
    session_id = state.session_id or "cart_session_default"
    cart_id = f"cart_{session_id}"
    wishlist_id = f"wishlist_{session_id}"

    # 1. Check for Wishlist Actions
    if state.intent == "wishlist_action":
        search_res = await store_client.search_products(ExtractedFilters(query=state.user_query))
        products = search_res.get("items", [])
        if products:
            target = products[0]
            await store_client.add_to_wishlist(wishlist_id, target["id"])
            wishlist_data = await store_client.get_wishlist(wishlist_id)
            response = f"💖 I've saved the **{target['title']}** (₹{target['base_price']:,.0f}) to your Wishlist for later!"
            ui_actions = [
                UIAction(action="SYNC_WISHLIST", payload=wishlist_data),
                UIAction(action="OPEN_WISHLIST_DRAWER", payload={"product_id": target["id"]}),
            ]
            return {
                "final_response": response,
                "ui_actions": ui_actions,
            }
        else:
            wishlist_data = await store_client.get_wishlist(wishlist_id)
            item_names = [it['title'] for it in wishlist_data.get('items', [])]
            if item_names:
                response = f"📋 Your wishlist currently has {len(item_names)} items:\n" + "\n".join([f"- **{name}**" for name in item_names])
            else:
                response = "Your wishlist is currently empty. Let me know which shoe you'd like to save!"
            return {
                "final_response": response,
                "ui_actions": [UIAction(action="OPEN_WISHLIST_DRAWER", payload={})],
            }

    # 2. View Cart Intent
    view_cart_phrases = ["view cart", "show cart", "what is in my cart", "what's in my cart", "check cart", "open cart"]
    is_view_cart = (any(k in query for k in view_cart_phrases) or query in ["cart", "my cart"]) and not any(k in query for k in ["add", "put", "insert", "buy", "place"])

    if is_view_cart:
        cart_data = await store_client.get_cart(cart_id)
        items = cart_data.get("items", [])
        if items:
            lines = [f"- **{it['title']}** (Size: {it.get('size', 'Standard')}) × {it['quantity']} — ₹{it['total_price']:,.0f}" for it in items]
            response = f"🛒 Here is what's in your cart ({cart_data.get('item_count', 0)} items, Subtotal: ₹{cart_data.get('subtotal', 0):,.0f}):\n\n" + "\n".join(lines)
        else:
            response = "🛒 Your cart is currently empty. Tell me what pair of shoes you'd like to add!"
        return {
            "final_response": response,
            "ui_actions": [UIAction(action="OPEN_CART_DRAWER", payload={})],
        }

    # 3. Add to Cart Mutation
    size_match = re.search(r'\b(?:size|uk)\s*(\d{1,2})\b', query)
    requested_size = size_match.group(1) if size_match else None

    # Search for product to add
    search_res = await store_client.search_products(ExtractedFilters(query=state.user_query))
    products = search_res.get("items", [])

    if not products:
        all_res = await store_client.search_products(ExtractedFilters())
        products = all_res.get("items", [])

    if products:
        target_product = products[0]
        variants = target_product.get("variants", [])

        target_variant = None
        if requested_size:
            for v in variants:
                if str(v.get("size")) == requested_size and v.get("stock", 0) > 0:
                    target_variant = v
                    break

        if not target_variant:
            for v in variants:
                if v.get("stock", 0) > 0:
                    target_variant = v
                    break

        if target_variant:
            await store_client.add_to_cart(
                cart_id=cart_id,
                product_id=target_product["id"],
                variant_id=target_variant["id"],
                quantity=1,
            )
            cart_data = await store_client.get_cart(cart_id)

            size_label = f" (Size {target_variant.get('size')})" if target_variant.get("size") else ""
            response = (
                f"🛍️ Added **{target_product['title']}**{size_label} to your bag for **₹{target_variant['price']:,.0f}**!\n\n"
                f"Your cart now has **{cart_data.get('item_count', 1)} items** (Subtotal: ₹{cart_data.get('subtotal', target_variant['price']):,.0f}). Ready to checkout?"
            )

            ui_actions = [
                UIAction(action="SYNC_CART", payload=cart_data),
                UIAction(action="OPEN_CART_DRAWER", payload={"product_id": target_product["id"]}),
                UIAction(action="HIGHLIGHT_PRODUCTS", payload={"product_ids": [target_product["id"]]}),
            ]
            return {
                "final_response": response,
                "ui_actions": ui_actions,
            }
        else:
            response = f"⚠️ I found the **{target_product['title']}**, but that item is currently out of stock. Would you like me to recommend similar alternatives?"
            return {"final_response": response, "ui_actions": []}

    return {
        "final_response": "I couldn't find the exact shoe you wanted to add. Could you mention the model name or brand (e.g., *'Add Nike Pegasus to cart'*)?",
        "ui_actions": [],
    }
