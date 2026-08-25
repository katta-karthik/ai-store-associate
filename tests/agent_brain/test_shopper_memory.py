"""Automated QA & Security Evaluation for Shopper Memory & Profile Store."""

import pytest
from httpx import AsyncClient
from agent_app.memory.shopper_memory import ShopperMemoryStore, ShopperProfile
from agent_app.memory.extractor import update_shopper_profile_from_query
from agent_app.graph.builder import shopagent_app


@pytest.mark.asyncio
async def test_shopper_memory_extraction_and_pii_sanitization(tmp_path):
    """Test extracting size, brand, budget, ergonomic notes, and PII masking."""
    db_file = str(tmp_path / "test_memory.db")
    store = ShopperMemoryStore(db_path=db_file)

    profile = ShopperProfile(shopper_id="shopper_test_001")
    
    # Query with preferences and a fake credit card / phone number
    query = "I wear size 10, love Nike running shoes under 9k, have knee pain, and my card is 4111 2222 3333 4444"
    updated_profile = update_shopper_profile_from_query(query, profile)

    assert updated_profile.preferred_size == "10"
    assert "Nike" in updated_profile.preferred_brands
    assert updated_profile.budget_max == 9000.0
    assert "Road Running" in updated_profile.preferred_categories
    assert any("knee" in n.lower() for n in updated_profile.special_notes)

    # Save to SQLite and verify PII Sanitization
    await store.save_profile(updated_profile)
    loaded = await store.get_profile("shopper_test_001")

    assert loaded.preferred_size == "10"
    assert loaded.budget_max == 9000.0
    # Verify card number was sanitized
    for note in loaded.special_notes:
        assert "4111" not in note


@pytest.mark.asyncio
async def test_shopper_memory_api_endpoints(agent_client: AsyncClient):
    """Test GET and DELETE /api/v1/shopper/{id}/memory."""
    shopper_id = "shopper_api_test_99"
    
    # 1. Retrieve initial profile
    res = await agent_client.get(f"/api/v1/shopper/{shopper_id}/memory")
    assert res.status_code == 200
    data = res.json()
    assert data["shopper_id"] == shopper_id

    # 2. Clear profile
    del_res = await agent_client.delete(f"/api/v1/shopper/{shopper_id}/memory")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True
