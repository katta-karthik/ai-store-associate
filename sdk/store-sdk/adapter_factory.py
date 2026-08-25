"""Universal Store Adapter Factory.

Dynamically instantiates and caches the appropriate e-commerce adapter
based on merchant configuration (Demo Store REST, Shopify Storefront GraphQL, WooCommerce, etc.).
"""

import os
from typing import Dict, Optional
try:
    from .universal_adapter import UniversalStoreAdapter
    from .demo_store_adapter import DemoStoreAdapter
    from .shopify_adapter import ShopifyStoreAdapter
    from .feed_adapter import CatalogFeedAdapter
except ImportError:
    from universal_adapter import UniversalStoreAdapter
    from demo_store_adapter import DemoStoreAdapter
    from shopify_adapter import ShopifyStoreAdapter
    from feed_adapter import CatalogFeedAdapter

_ADAPTER_REGISTRY: Dict[str, UniversalStoreAdapter] = {}


def get_store_adapter(
    adapter_type: Optional[str] = None,
    store_api_url: Optional[str] = None,
    shopify_domain: Optional[str] = None,
    shopify_token: Optional[str] = None,
    feed_url: Optional[str] = None,
) -> UniversalStoreAdapter:
    """Factory method to get or instantiate a UniversalStoreAdapter.

    Args:
        adapter_type: 'demo', 'shopify', 'feed', or 'rest' (defaults to STORE_ADAPTER_TYPE env var).
        store_api_url: Base REST API URL for demo or custom REST stores.
        shopify_domain: Shopify store domain (e.g. 'mystore.myshopify.com').
        shopify_token: Shopify Storefront API access token.
        feed_url: Catalog feed JSON/XML URL for zero-backend custom stores.
    """
    adapter_type = (
        adapter_type or os.getenv("STORE_ADAPTER_TYPE", "demo")
    ).lower().strip()

    cache_key = f"{adapter_type}_{feed_url or store_api_url or shopify_domain or 'default'}"
    if cache_key in _ADAPTER_REGISTRY:
        return _ADAPTER_REGISTRY[cache_key]

    if adapter_type == "shopify":
        domain = shopify_domain or os.getenv("SHOPIFY_STORE_DOMAIN", "")
        token = shopify_token or os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
        adapter = ShopifyStoreAdapter(store_domain=domain, storefront_access_token=token)
    elif adapter_type == "feed":
        f_url = feed_url or os.getenv("CATALOG_FEED_URL", "http://localhost:8000/api/v1/products")
        adapter = CatalogFeedAdapter(feed_url=f_url)
    else:
        # Default to Demo/REST store adapter
        base_url = store_api_url or os.getenv("STORE_API_URL", "http://localhost:8000/api/v1")
        adapter = DemoStoreAdapter(base_url=base_url)

    _ADAPTER_REGISTRY[cache_key] = adapter
    return adapter
