"""Automated QA & AI Evaluation Tests for LangGraph Search & Entity Extraction."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from agent_app.graph.builder import shopagent_app
from agent_app.schemas.agent_state import ShopAgentState


MOCK_PRODUCTS_DATA = [
    {
        "id": "prod_nike_pegasus_41",
        "title": "Nike Air Zoom Pegasus 41",
        "brand": "Nike",
        "category": "Running Shoes",
        "base_price": 7899.0,
        "description": "Responsive road running shoes with Air Zoom cushioning.",
        "primary_image": "https://example.com/pegasus.jpg",
        "variants": [{"id": "var_1", "size": "10", "price": 7899.0, "stock": 10}]
    },
    {
        "id": "prod_adidas_ub",
        "title": "Adidas Ultraboost Light",
        "brand": "Adidas",
        "category": "Running Shoes",
        "base_price": 7499.0,
        "description": "Energy return running shoes.",
        "primary_image": "https://example.com/ub.jpg",
        "variants": [{"id": "var_2", "size": "10", "price": 7499.0, "stock": 5}]
    }
]


@pytest.mark.asyncio
async def test_agent_graph_general_greeting():
    """Verify greeting query routes to general_chat without calling search tool."""
    state = ShopAgentState(user_query="Hello! Who are you?")
    result = await shopagent_app.ainvoke(state)

    assert result["intent"] == "general_chat"
    assert "walking with you" in result["final_response"].lower() or "sales" in result["final_response"].lower()
    assert len(result["ui_actions"]) == 0


@pytest.mark.asyncio
async def test_agent_graph_search_extraction_price_and_category():
    """Verify 'running shoes under 8k' extracts max_price=8000 and category=running-shoes."""
    with patch("agent_app.tools.store_tools.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"total": 2, "items": MOCK_PRODUCTS_DATA}

        state = ShopAgentState(user_query="I need running shoes under 8k in size 10")
        result = await shopagent_app.ainvoke(state)

        assert result["intent"] == "product_search"
        filters = result["extracted_filters"]
        assert filters.category_id == "running-shoes"
        assert filters.max_price == 8000.0
        assert filters.size == "10"

        # Verify UI Action was generated to update storefront filters
        ui_actions = result["ui_actions"]
        assert len(ui_actions) >= 1
        set_filter_action = next((a for a in ui_actions if a.action == "SET_FILTERS"), None)
        assert set_filter_action is not None
        assert set_filter_action.payload["category"] == "running-shoes"
        assert set_filter_action.payload["max_price"] == 8000.0

        # Verify Salesperson consultative response
        assert "Nike Air Zoom Pegasus 41" in result["final_response"]


@pytest.mark.asyncio
async def test_agent_chat_api_endpoint(agent_client: AsyncClient):
    """Verify REST API /api/v1/chat/message returns structured envelope."""
    with patch("agent_app.tools.store_tools.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"total": 2, "items": MOCK_PRODUCTS_DATA}

        payload = {
            "session_id": "test_session_123",
            "message": "Show me Nike road running shoes",
        }
        resp = await agent_client.post("/api/v1/chat/message", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "test_session_123"
        assert data["intent"] == "product_search"
        assert len(data["products"]) == 2
        assert len(data["ui_actions"]) >= 1
