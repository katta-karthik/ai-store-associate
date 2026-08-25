"""Automated QA & AI Evaluation for Deep Shopping Research Agent."""

import pytest
from unittest.mock import patch, AsyncMock
from agent_app.graph.builder import shopagent_app
from agent_app.schemas.agent_state import ShopAgentState


@pytest.mark.asyncio
async def test_deep_research_multi_constraint_routing_and_scoring():
    """Test multi-constraint marathon, flat feet, and hybrid terrain synthesis."""
    p1 = {
        "id": "prod_nike_pegasus_40",
        "title": "Nike Air Zoom Pegasus 40",
        "brand": "Nike",
        "description": "Daily road running shoe with dual Zoom Air units for shock absorption.",
        "base_price": 9495.0,
        "specs": {"cushioning": "Zoom Air", "weight": "288g"},
    }
    p2 = {
        "id": "prod_salomon_speedcross_6",
        "title": "Salomon Speedcross 6 GTX",
        "brand": "Salomon",
        "description": "Trail running shoe with deep lug traction and waterproof Gore-Tex.",
        "base_price": 14999.0,
        "specs": {"cushioning": "EnergyCell+", "weight": "328g"},
    }

    with patch("agent_app.graph.nodes.deep_research.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"items": [p1, p2], "total": 2}

        state = ShopAgentState(
            user_query="I have flat feet and am training for my first marathon under 12k with gravel trails",
            session_id="test_research_session",
            shopper_id="shopper_res_001",
        )

        result = await shopagent_app.ainvoke(state)

        assert result["intent"] == "deep_research"
        assert "Hero Match" in result["final_response"]
        assert "Match" in result["final_response"]

        # Verify SHOW_RESEARCH_REPORT UI Action was dispatched
        action_names = [a.action for a in result["ui_actions"]]
        assert "SHOW_RESEARCH_REPORT" in action_names
        
        report_action = next(a for a in result["ui_actions"] if a.action == "SHOW_RESEARCH_REPORT")
        top_product = report_action.payload["top_product"]
        assert top_product["match_score"] > 80
        assert len(top_product["pros"]) > 0
