"""Automated Tests for CatalogFeedAdapter."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath("sdk/store-sdk"))

from feed_adapter import CatalogFeedAdapter
from universal_adapter import ProductSearchParams
from adapter_factory import get_store_adapter


@pytest.mark.asyncio
async def test_feed_adapter_catalog_sync_and_search():
    """Verify CatalogFeedAdapter ingests standard JSON product feed and searches with filters."""
    adapter = CatalogFeedAdapter(feed_url="https://mystore.com/products.json")

    mock_feed = [
        {
            "id": "item_101",
            "title": "Spring Boot Marathon Runner",
            "brand": "Nike",
            "category": "Road Running",
            "price": 8999.0,
            "images": ["https://example.com/shoe.jpg"],
            "tags": ["marathon", "cushion"],
            "variants": [
                {"id": "var_101_10", "size": "UK 10", "price": 8999.0, "stock": 5}
            ]
        }
    ]

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_feed

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await adapter.search_products(ProductSearchParams(query="Marathon"))

        assert res.total == 1
        assert res.items[0].title == "Spring Boot Marathon Runner"
        assert res.items[0].brand == "Nike"
        assert res.items[0].base_price == 8999.0


@pytest.mark.asyncio
async def test_adapter_factory_feed_instantiation():
    """Verify Adapter Factory instantiates CatalogFeedAdapter with custom feed URL."""
    feed_adapter = get_store_adapter(adapter_type="feed", feed_url="https://theirstore.com/catalog.json")
    assert isinstance(feed_adapter, CatalogFeedAdapter)
    assert feed_adapter.feed_url == "https://theirstore.com/catalog.json"
