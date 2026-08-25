"""Automated QA & Chaos Tests for Cart API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_empty_cart(async_client: AsyncClient):
    """Verify newly initialized cart has 0 items and 0 subtotal."""
    resp = await async_client.get("/api/v1/cart/test_cart_001")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cart_id"] == "test_cart_001"
    assert data["item_count"] == 0
    assert data["subtotal"] == 0.0


@pytest.mark.asyncio
async def test_add_item_to_cart_success(async_client: AsyncClient):
    """Verify adding an in-stock product variant to cart."""
    payload = {
        "product_id": "prod_nike_pegasus_41",
        "variant_id": "var_peg_blk_10",
        "quantity": 1,
    }
    resp = await async_client.post("/api/v1/cart/test_cart_002/items", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["item_count"] == 1
    assert data["subtotal"] == 10495.0
    assert len(data["items"]) == 1
    assert "Pegasus" in data["items"][0]["title"]


@pytest.mark.asyncio
async def test_add_non_existent_variant_rejected(async_client: AsyncClient):
    """Verify adding an invalid/non-existent variant is rejected with 400 Bad Request."""
    payload = {
        "product_id": "prod_adidas_ultraboost_light",
        "variant_id": "var_non_existent_999",
        "quantity": 1,
    }
    resp = await async_client.post("/api/v1/cart/test_cart_003/items", json=payload)
    assert resp.status_code in [400, 404]
    assert "Variant" in resp.json()["detail"] or "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_remove_item_from_cart(async_client: AsyncClient):
    """Verify removing an item from the cart."""
    # 1. Add item first
    add_payload = {
        "product_id": "prod_puma_nitro_elite_3",
        "variant_id": "var_pum_nit_9",
        "quantity": 2,
    }
    add_resp = await async_client.post("/api/v1/cart/test_cart_004/items", json=add_payload)
    assert add_resp.status_code == 200
    item_id = add_resp.json()["data"]["items"][0]["item_id"]

    # 2. Remove item
    del_resp = await async_client.delete(f"/api/v1/cart/test_cart_004/items/{item_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["item_count"] == 0
    assert del_resp.json()["data"]["subtotal"] == 0.0
