"""Automated Tests for ShopifyStoreAdapter."""

import pytest
from unittest.mock import patch, AsyncMock
import sys
import os

# Add sdk to path
sys.path.insert(0, os.path.abspath("sdk/store-sdk"))

from shopify_adapter import ShopifyStoreAdapter
from universal_adapter import ProductSearchParams


@pytest.mark.asyncio
async def test_shopify_adapter_search_products():
    """Test Shopify GraphQL query parsing into normalized ProductDTOs."""
    adapter = ShopifyStoreAdapter("myshop.myshopify.com", "fake_storefront_token")

    fake_gql_response = {
        "data": {
            "products": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/Product/123",
                            "title": "Shopify Pegasus Runner",
                            "vendor": "Nike",
                            "productType": "Road Running",
                            "description": "High performance runner",
                            "priceRange": {
                                "minVariantPrice": {
                                    "amount": "8999.00",
                                    "currencyCode": "INR",
                                }
                            },
                            "images": {
                                "edges": [{"node": {"url": "https://cdn.shopify.com/shoe.png"}}]
                            },
                            "variants": {
                                "edges": [
                                    {
                                        "node": {
                                            "id": "gid://shopify/ProductVariant/456",
                                            "title": "UK 10",
                                            "price": {"amount": "8999.00"},
                                            "availableForSale": True,
                                            "quantityAvailable": 5,
                                        }
                                    }
                                ]
                            },
                        }
                    }
                ]
            }
        }
    }

    with patch.object(adapter, "_execute_graphql", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = fake_gql_response

        res = await adapter.search_products(ProductSearchParams(query="Pegasus"))

        assert res.total == 1
        item = res.items[0]
        assert item.title == "Shopify Pegasus Runner"
        assert item.brand == "Nike"
        assert item.base_price == 8999.00
        assert len(item.variants) == 1
        assert item.variants[0].size == "UK 10"
