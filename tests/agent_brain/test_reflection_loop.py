"""Automated QA & AI Evaluation Tests for LangGraph Reflection & Self-Critique Loop."""

import pytest
from unittest.mock import AsyncMock, patch
from agent_app.graph.builder import shopagent_app
from agent_app.graph.nodes.reflection_evaluator import reflection_evaluator_node
from agent_app.schemas.agent_state import ExtractedFilters, ShopAgentState

MOCK_PRODUCTS = [
    {
        "id": "prod_nike_pegasus_41",
        "title": "Nike Air Zoom Pegasus 41",
        "brand": "Nike",
        "category": "Running Shoes",
        "base_price": 7899.0,
        "description": "High cushioning road running shoes with ReactX foam.",
        "primary_image": "https://example.com/pegasus.jpg",
        "variants": [
            {"id": "var_1", "size": "10", "price": 7899.0, "stock": 5},
            {"id": "var_2", "size": "9", "price": 7899.0, "stock": 0},
        ],
    },
    {
        "id": "prod_adidas_ub",
        "title": "Adidas Ultraboost Light",
        "brand": "Adidas",
        "category": "Running Shoes",
        "base_price": 8499.0,
        "description": "Max cushioning energy return running shoe.",
        "primary_image": "https://example.com/ub.jpg",
        "variants": [
            {"id": "var_3", "size": "10", "price": 8499.0, "stock": 2},
        ],
    },
]


@pytest.mark.asyncio
async def test_reflection_evaluator_within_budget():
    """Verify reflection node validates within-budget products and sets high confidence score."""
    state = ShopAgentState(
        user_query="I need running shoes under 8000 in size 10",
        extracted_filters=ExtractedFilters(max_price=8000.0, size="10"),
        retrieved_products=MOCK_PRODUCTS,
    )
    result = await reflection_evaluator_node(state)

    assert len(result["retrieved_products"]) == 1
    assert result["retrieved_products"][0]["id"] == "prod_nike_pegasus_41"
    assert result["confidence_score"] >= 0.90
    assert any("budget" in n.lower() for n in result["reflection_notes"])
    assert any("size uk 10" in n.lower() for n in result["reflection_notes"])


@pytest.mark.asyncio
async def test_reflection_evaluator_cushion_prioritization():
    """Verify conceptual intent (cushion/comfort) is recognized and prioritized in reflection."""
    state = ShopAgentState(
        user_query="I need extra comfort and cushion for long runs",
        extracted_filters=ExtractedFilters(),
        retrieved_products=MOCK_PRODUCTS,
    )
    result = await reflection_evaluator_node(state)

    assert result["confidence_score"] >= 0.90
    assert any("cushion" in n.lower() for n in result["reflection_notes"])


@pytest.mark.asyncio
async def test_full_langgraph_reflection_loop_integration():
    """Verify end-to-end LangGraph execution traverses search_extractor -> reflection_evaluator -> salesperson."""
    with patch("agent_app.tools.store_tools.store_client.search_products", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {"total": 2, "items": MOCK_PRODUCTS}

        state = ShopAgentState(user_query="Looking for road running shoes under 8500 in size 10")
        result = await shopagent_app.ainvoke(state)

        assert result["intent"] == "product_search"
        assert len(result["retrieved_products"]) >= 1
        assert "reflection_notes" in result
        assert len(result["reflection_notes"]) >= 1
        assert result["confidence_score"] > 0.0
