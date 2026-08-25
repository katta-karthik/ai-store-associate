"""Automated QA & AI Evaluation for Product Comparison & Fit Advisor."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from agent_app.graph.builder import shopagent_app
from agent_app.schemas.agent_state import ShopAgentState


@pytest.mark.asyncio
async def test_product_comparison_routing_and_modal_dispatch():
    """Test 'Compare Nike Pegasus vs Adidas Ultraboost' execution and OPEN_COMPARISON_MODAL UI action."""
    p1 = {
        "id": "prod_nike_pegasus_40",
        "title": "Nike Air Zoom Pegasus 40",
        "brand": "Nike",
        "base_price": 9495.0,
        "specs": {"cushioning": "Zoom Air", "weight": "288g", "heel_drop": "10mm"},
    }
    p2 = {
        "id": "prod_adidas_ultraboost_light",
        "title": "Adidas Ultraboost Light",
        "brand": "Adidas",
        "base_price": 13999.0,
        "specs": {"cushioning": "Light BOOST", "weight": "299g", "heel_drop": "10mm"},
    }

    with patch("agent_app.graph.nodes.product_comparator.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"items": [p1, p2], "total": 2}

        state = ShopAgentState(
            user_query="Compare Nike Pegasus vs Adidas Ultraboost",
            session_id="test_compare_session",
            shopper_id="shopper_comp_001",
        )

        result = await shopagent_app.ainvoke(state)

        assert result["intent"] == "compare_products"
        assert "Side-by-Side Comparison" in result["final_response"]
        assert "Zoom Air" in result["final_response"]
        assert "Light BOOST" in result["final_response"]
        
        # Verify OPEN_COMPARISON_MODAL action was dispatched
        action_names = [a.action for a in result["ui_actions"]]
        assert "OPEN_COMPARISON_MODAL" in action_names
        
        modal_action = next(a for a in result["ui_actions"] if a.action == "OPEN_COMPARISON_MODAL")
        assert len(modal_action.payload["products"]) == 2


@pytest.mark.asyncio
async def test_fit_advice_heuristic():
    """Test fit advice generation when comparing technical trail shoes."""
    p1 = {
        "id": "prod_salomon_speedcross_6",
        "title": "Salomon Speedcross 6 GTX",
        "brand": "Salomon",
        "base_price": 14999.0,
        "specs": {"cushioning": "EnergyCell+", "weight": "328g"},
    }
    p2 = {
        "id": "prod_nike_pegasus_40",
        "title": "Nike Air Zoom Pegasus 40",
        "brand": "Nike",
        "base_price": 9495.0,
        "specs": {"cushioning": "Zoom Air", "weight": "288g"},
    }

    with patch("agent_app.graph.nodes.product_comparator.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"items": [p1, p2], "total": 2}

        state = ShopAgentState(
            user_query="Which is better for trails: Salomon or Nike?",
            session_id="test_trail_session",
            shopper_id="shopper_comp_002",
        )

        result = await shopagent_app.ainvoke(state)

        assert result["intent"] == "compare_products"
        assert "Fit Advice" in result["final_response"]
        assert "half a size up" in result["final_response"].lower()
