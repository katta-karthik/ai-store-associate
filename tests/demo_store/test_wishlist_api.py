"""Automated QA Test Suite for Wishlist API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_empty_wishlist(async_client: AsyncClient):
    """Test retrieving an initial empty wishlist."""
    response = await async_client.get("/api/v1/wishlist/test_wl_001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["wishlist_id"] == "test_wl_001"
    assert data["data"]["item_count"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_add_item_to_wishlist_success(async_client: AsyncClient):
    """Test adding a valid product to wishlist."""
    # First get product id from products endpoint
    prod_resp = await async_client.get("/api/v1/products")
    products = prod_resp.json()["data"]["items"]
    assert len(products) > 0
    target_product = products[0]

    # Add to wishlist
    payload = {"product_id": target_product["id"]}
    response = await async_client.post("/api/v1/wishlist/test_wl_002/items", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["item_count"] == 1
    assert data["data"]["items"][0]["product_id"] == target_product["id"]


@pytest.mark.asyncio
async def test_remove_item_from_wishlist(async_client: AsyncClient):
    """Test removing an item from the wishlist."""
    prod_resp = await async_client.get("/api/v1/products")
    target_product = prod_resp.json()["data"]["items"][0]

    # Add item
    add_resp = await async_client.post(
        "/api/v1/wishlist/test_wl_003/items",
        json={"product_id": target_product["id"]},
    )
    wishlist_data = add_resp.json()["data"]
    item_id = wishlist_data["items"][0]["item_id"]

    # Delete item
    del_resp = await async_client.delete(f"/api/v1/wishlist/test_wl_003/items/{item_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["item_count"] == 0
