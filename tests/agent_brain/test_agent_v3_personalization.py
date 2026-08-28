"""Automated Unit Tests for ShopAgent v3.0 AI Hyper-Personalization Engine."""

import pytest
import os
from unittest.mock import patch, AsyncMock
from agent_app.memory.shopper_memory import ShopperProfile, ShopperMemoryStore
from agent_app.memory.conversation_store import ConversationStore
from agent_app.memory.extractor import update_shopper_profile_from_query_regex
from agent_app.schemas.agent_state import ExtractedFilters, ProductPersonalizationScore, ShopAgentState
from agent_app.graph.nodes.reflection_evaluator import reflection_evaluator_node


@pytest.mark.asyncio
async def test_shopper_profile_v3_deep_fields(tmp_path):
    """Test v3.0 deep personalization fields, serialization, and context generation."""
    db_path = str(tmp_path / "test_memory.db")
    store = ShopperMemoryStore(db_path=db_path)

    profile = ShopperProfile(
        shopper_id="shopper_vip_99",
        preferred_brands=["Nike", "Salomon"],
        preferred_size="10",
        budget_max=12000.0,
        style_dna=["minimalist", "bold"],
        preferred_colors=["black", "white"],
        foot_conditions=["wide feet", "knee pain"],
        use_cases=["marathon training"],
        occasion_history=["anniversary gift"],
        disliked_brands=["Puma"],
        price_sensitivity="premium",
        sentiment_trend="enthusiastic",
    )

    await store.save_profile(profile)
    loaded = await store.get_profile("shopper_vip_99")

    assert loaded.shopper_id == "shopper_vip_99"
    assert "Nike" in loaded.preferred_brands
    assert "Salomon" in loaded.preferred_brands
    assert loaded.preferred_size == "10"
    assert loaded.budget_max == 12000.0
    assert "wide feet" in loaded.foot_conditions
    assert "knee pain" in loaded.foot_conditions
    assert "Puma" in loaded.disliked_brands
    assert loaded.price_sensitivity == "premium"

    context = loaded.get_personalization_context()
    assert "Shoe size: UK 10" in context
    assert "Favorite brands: Nike, Salomon" in context
    assert "Dislikes: Puma" in context
    assert "Foot conditions: wide feet, knee pain" in context


@pytest.mark.asyncio
async def test_conversation_store_multi_turn(tmp_path):
    """Test conversation history persistence and LLM transcript formatting."""
    db_path = str(tmp_path / "test_conv.db")
    conv_store = ConversationStore(db_path=db_path)

    session_id = "test_session_123"
    shopper_id = "shopper_vip_99"

    # Add turn 1
    await conv_store.add_message(
        session_id=session_id,
        shopper_id=shopper_id,
        role="user",
        content="Show me Nike running shoes under 10000",
    )
    await conv_store.add_message(
        session_id=session_id,
        shopper_id=shopper_id,
        role="assistant",
        content="Here are 2 Nike running shoes for you, Sir!",
        intent="product_search",
        product_ids=["prod_1", "prod_2"],
    )

    # Add turn 2
    await conv_store.add_message(
        session_id=session_id,
        shopper_id=shopper_id,
        role="user",
        content="Something cheaper in black?",
    )

    history = await conv_store.get_history(session_id)
    assert len(history) == 3
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[2]["content"] == "Something cheaper in black?"

    # Check transcript formatting
    formatted = conv_store.format_history_for_llm(history)
    assert 'Customer: "Show me Nike running shoes under 10000"' in formatted
    assert 'Associate: "Here are 2 Nike running shoes for you, Sir!" [showed 2 products]' in formatted
    assert 'Customer: "Something cheaper in black?"' in formatted


def test_preference_extractor_v3_regex():
    """Test regex extraction of brands, negative signals, foot conditions, and use cases."""
    profile = ShopperProfile(shopper_id="test_user")

    query = "I have knee pain and wide feet, training for my first marathon. Prefer Nike and Asics, but don't like Puma. Budget under 9000 size 11 in black."
    updated = update_shopper_profile_from_query_regex(query, profile)

    assert updated.preferred_size == "11"
    assert updated.budget_max == 9000.0
    assert "Nike" in updated.preferred_brands
    assert "Asics" in updated.preferred_brands
    assert "Puma" in updated.disliked_brands
    assert "knee pain" in updated.foot_conditions
    assert "wide feet" in updated.foot_conditions
    assert "marathon training" in updated.use_cases
    assert "black" in updated.preferred_colors


@pytest.mark.asyncio
async def test_reflection_evaluator_personalization_scoring():
    """Test that reflection_evaluator_node produces structured personalization scores."""
    profile = ShopperProfile(
        shopper_id="test_user",
        preferred_brands=["Nike"],
        preferred_size="10",
        budget_max=10000.0,
        foot_conditions=["knee pain"],
    )

    products = [
        {
            "id": "prod_nike_zoom",
            "title": "Nike Air Zoom Pegasus 40",
            "brand": "Nike",
            "base_price": 9495.0,
            "description": "High cushioning ReactX foam and Zoom Air unit for knee comfort",
            "variants": [{"size": "10", "stock": 5, "price": 9495.0}],
        },
        {
            "id": "prod_salomon_speed",
            "title": "Salomon Speedcross 6",
            "brand": "Salomon",
            "base_price": 14999.0,
            "description": "Aggressive trail grip",
            "variants": [{"size": "10", "stock": 3, "price": 14999.0}],
        },
    ]

    state = ShopAgentState(
        session_id="test_sess",
        shopper_id="test_user",
        user_query="I need high cushion running shoes for knee pain under 10000",
        shopper_profile=profile,
        extracted_filters=ExtractedFilters(max_price=10000.0, size="10"),
        retrieved_products=products,
    )

    res = await reflection_evaluator_node(state)

    assert "retrieved_products" in res
    assert "personalization_scores" in res
    scores = res["personalization_scores"]
    assert len(scores) > 0

    top_score = scores[0]
    assert top_score.product_id == "prod_nike_zoom"
    assert top_score.score >= 0.8
    assert len(top_score.match_factors) > 0
    assert any("Fits your ₹10,000 budget" in f or "Nike" in f for f in top_score.match_factors)
