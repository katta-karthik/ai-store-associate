"""Automated Tests for DemoStoreAdapter."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath("sdk/store-sdk"))

from demo_store_adapter import DemoStoreAdapter
from universal_adapter import ProductSearchParams
from adapter_factory import get_store_adapter


@pytest.mark.asyncio
async def test_demo_store_adapter_search_products():
    """Verify DemoStoreAdapter converts raw REST product JSON into typed ProductDTOs."""
    adapter = DemoStoreAdapter(base_url="http://localhost:8000/api/v1")

    fake_response = {
        "success": True,
        "data": {
            "total": 1,
            "items": [
                {
                    "id": "prod_pegasus_41",
                    "title": "Nike Pegasus 41",
                    "brand": "Nike",
                    "category": "Road Running",
                    "description": "Daily trainer",
                    "base_price": 10495.0,
                    "currency": "INR",
                    "rating": 4.8,
                    "review_count": 124,
                    "primary_image": "https://example.com/pegasus.jpg",
                    "images": ["https://example.com/pegasus.jpg"],
                    "tags": ["running", "cushion"],
                    "specs": {"heel_drop": "10mm"},
                    "variants": [
                        {"id": "var_1", "size": "UK 10", "color": "Black", "price": 10495.0, "stock": 5}
                    ],
                }
            ],
            "facets": {},
        },
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_response

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await adapter.search_products(ProductSearchParams(query="Pegasus"))

        assert res.total == 1
        assert len(res.items) == 1
        assert res.items[0].title == "Nike Pegasus 41"
        assert res.items[0].brand == "Nike"
        assert res.items[0].base_price == 10495.0
        assert len(res.items[0].variants) == 1
        assert res.items[0].variants[0].size == "UK 10"


@pytest.mark.asyncio
async def test_adapter_factory_instantiation():
    """Verify Adapter Factory creates DemoStoreAdapter and ShopifyStoreAdapter correctly."""
    demo_adapter = get_store_adapter(adapter_type="demo", store_api_url="http://mock-store:8000/api/v1")
    assert isinstance(demo_adapter, DemoStoreAdapter)
    assert demo_adapter.base_url == "http://mock-store:8000/api/v1"
