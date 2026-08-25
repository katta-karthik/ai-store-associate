"""ShopAgent Universal Store SDK & Commerce Adapters."""

from .universal_adapter import (
    CartDTO,
    CartItemDTO,
    ProductDTO,
    ProductSearchParams,
    ProductSearchResultDTO,
    ProductVariantDTO,
    UniversalStoreAdapter,
    WishlistDTO,
    WishlistItemDTO,
)
from .demo_store_adapter import DemoStoreAdapter
from .shopify_adapter import ShopifyStoreAdapter
from .feed_adapter import CatalogFeedAdapter
from .adapter_factory import get_store_adapter

__all__ = [
    "UniversalStoreAdapter",
    "ProductDTO",
    "ProductVariantDTO",
    "ProductSearchParams",
    "ProductSearchResultDTO",
    "CartDTO",
    "CartItemDTO",
    "WishlistDTO",
    "WishlistItemDTO",
    "DemoStoreAdapter",
    "ShopifyStoreAdapter",
    "CatalogFeedAdapter",
    "get_store_adapter",
]
