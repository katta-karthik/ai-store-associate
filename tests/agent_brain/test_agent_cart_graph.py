"""Automated QA & AI Evaluation for Conversational Cart & Wishlist LangGraph Actions."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from agent_app.graph.builder import shopagent_app


@pytest.mark.asyncio
async def test_agent_graph_cart_action_routing():
    """Test conversational 'Add Nike Pegasus size 10 to cart' routing and UI action generation."""
    mock_product = {
        "id": "prod_nike_pegasus_40",
        "title": "Nike Air Zoom Pegasus 40",
        "base_price": 9495.0,
        "variants": [
            {"id": "var_nike_peg_10", "size": "10", "stock": 5, "price": 9495.0}
        ],
    }
    mock_cart = {
        "cart_id": "cart_test_session",
        "items": [
            {"item_id": "item_1", "title": "Nike Air Zoom Pegasus 40", "quantity": 1, "total_price": 9495.0}
        ],
        "item_count": 1,
        "subtotal": 9495.0,
    }

    with patch("agent_app.graph.nodes.cart_manager.store_client.search_products", new_callable=AsyncMock) as mock_search, \
         patch("agent_app.graph.nodes.cart_manager.store_client.add_to_cart", new_callable=AsyncMock) as mock_add, \
         patch("agent_app.graph.nodes.cart_manager.store_client.get_cart", new_callable=AsyncMock) as mock_get:
        
        mock_search.return_value = {"items": [mock_product], "total": 1}
        mock_add.return_value = mock_cart
        mock_get.return_value = mock_cart

        input_state = {
            "session_id": "test_session",
            "user_query": "Add Nike Pegasus size 10 to my cart",
            "messages": [],
        }

        output_state = await shopagent_app.ainvoke(input_state)

        assert output_state["intent"] == "cart_action"
        assert "Nike Air Zoom Pegasus 40" in output_state["final_response"]
        assert len(output_state["ui_actions"]) > 0
        action_names = [a.action for a in output_state["ui_actions"]]
        assert "SYNC_CART" in action_names
        assert "OPEN_CART_DRAWER" in action_names


@pytest.mark.asyncio
async def test_agent_graph_wishlist_action():
    """Test conversational 'Save Salomon to wishlist' execution."""
    mock_product = {
        "id": "prod_salomon_speedcross_6",
        "title": "Salomon Speedcross 6 GTX",
        "base_price": 14999.0,
        "variants": [{"id": "var_salomon_10", "size": "10", "stock": 4, "price": 14999.0}],
    }
    mock_wishlist = {
        "wishlist_id": "wishlist_test_session",
        "items": [{"item_id": "witem_1", "product_id": "prod_salomon_speedcross_6", "title": "Salomon Speedcross 6 GTX"}],
        "item_count": 1,
    }

    with patch("agent_app.graph.nodes.cart_manager.store_client.search_products", new_callable=AsyncMock) as mock_search, \
         patch("agent_app.graph.nodes.cart_manager.store_client.add_to_wishlist", new_callable=AsyncMock) as mock_add, \
         patch("agent_app.graph.nodes.cart_manager.store_client.get_wishlist", new_callable=AsyncMock) as mock_get:

        mock_search.return_value = {"items": [mock_product], "total": 1}
        mock_add.return_value = mock_wishlist
        mock_get.return_value = mock_wishlist

        input_state = {
            "session_id": "test_session",
            "user_query": "Save this Salomon shoe to my wishlist",
            "messages": [],
        }

        output_state = await shopagent_app.ainvoke(input_state)

        assert output_state["intent"] == "wishlist_action"
        assert "Wishlist" in output_state["final_response"]
        action_names = [a.action for a in output_state["ui_actions"]]
        assert "SYNC_WISHLIST" in action_names
