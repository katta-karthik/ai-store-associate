"""Automated QA & Chaos Tests for Products API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(async_client: AsyncClient):
    """Verify SRE health probes (liveness and readiness)."""
    live_resp = await async_client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "live"

    ready_resp = await async_client.get("/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_list_products_all(async_client: AsyncClient):
    """Verify listing all products returns seeded catalog."""
    resp = await async_client.get("/api/v1/products")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["total"] >= 5
    assert len(data["data"]["items"]) >= 5


@pytest.mark.asyncio
async def test_search_products_by_text(async_client: AsyncClient):
    """Verify search filter with query 'Pegasus'."""
    resp = await async_client.get("/api/v1/products?q=Pegasus")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Nike Air Zoom Pegasus 41"


@pytest.mark.asyncio
async def test_filter_products_by_price_range(async_client: AsyncClient):
    """Verify price range filtering (e.g. min 7000, max 8000)."""
    resp = await async_client.get("/api/v1/products?min_price=7000&max_price=8000")
    assert resp.status_code == 200
    data = resp.json()["data"]
    for item in data["items"]:
        assert 7000 <= item["base_price"] <= 8000


@pytest.mark.asyncio
async def test_filter_products_by_category(async_client: AsyncClient):
    """Verify category filtering by slug."""
    resp = await async_client.get("/api/v1/products?category_id=trail-outdoor")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["brand"] == "Salomon"


@pytest.mark.asyncio
async def test_get_product_detail_success(async_client: AsyncClient):
    """Verify retrieving single product detail with specs and variants."""
    resp = await async_client.get("/api/v1/products/prod_nike_pegasus_41")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == "prod_nike_pegasus_41"
    assert "weight_grams" in data["specs"]
    assert len(data["variants"]) >= 3


@pytest.mark.asyncio
async def test_get_product_detail_not_found(async_client: AsyncClient):
    """Verify 404 response for non-existent product ID (Edge case)."""
    resp = await async_client.get("/api/v1/products/prod_non_existent_999")
    assert resp.status_code == 404
