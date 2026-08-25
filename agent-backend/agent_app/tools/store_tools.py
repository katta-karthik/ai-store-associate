"""Store Tool Handlers interacting with the Universal Commerce Adapter SDK."""

import sys
import os
from typing import Any, Dict, List, Optional
from agent_app.core.config import settings
from agent_app.schemas.agent_state import ExtractedFilters

# Ensure SDK is in python path
sdk_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sdk/store-sdk"))
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

try:
    from adapter_factory import get_store_adapter
    from universal_adapter import ProductSearchParams, UniversalStoreAdapter
except ImportError:
    from sdk.store_sdk.adapter_factory import get_store_adapter
    from sdk.store_sdk.universal_adapter import ProductSearchParams, UniversalStoreAdapter


class StoreAPIClient:
    """Store Client utilizing Universal Store Adapter SDK."""

    def __init__(self, adapter: Optional[UniversalStoreAdapter] = None):
        self.adapter = adapter or get_store_adapter(
            adapter_type=settings.STORE_ADAPTER_TYPE,
            store_api_url=settings.STORE_API_URL,
            shopify_domain=settings.SHOPIFY_STORE_DOMAIN,
            shopify_token=settings.SHOPIFY_STOREFRONT_TOKEN,
        )

    async def search_products(self, filters: ExtractedFilters) -> Dict[str, Any]:
        """Search products using the configured Store Adapter."""
        params = ProductSearchParams(
            query=filters.query,
            category_id=filters.category_id,
            min_price=filters.min_price,
            max_price=filters.max_price,
            brand=filters.brand,
            size=filters.size,
            in_stock=True,
        )
        res = await self.adapter.search_products(params)
        return {
            "total": res.total,
            "items": [it.model_dump() for it in res.items],
            "facets": res.facets,
        }

    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single product detail via Store Adapter."""
        product = await self.adapter.get_product_by_id(product_id)
        return product.model_dump() if product else None

    # Cart Operations
    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        """Fetch cart via Store Adapter."""
        cart = await self.adapter.get_cart(cart_id)
        return cart.model_dump()

    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> Dict[str, Any]:
        """Add item to cart via Store Adapter."""
        cart = await self.adapter.add_to_cart(cart_id, product_id, variant_id, quantity)
        return cart.model_dump()

    async def remove_from_cart(self, cart_id: str, item_id: str) -> Dict[str, Any]:
        """Remove item from cart via Store Adapter."""
        cart = await self.adapter.remove_from_cart(cart_id, item_id)
        return cart.model_dump()

    # Wishlist Operations
    async def get_wishlist(self, wishlist_id: str) -> Dict[str, Any]:
        """Fetch wishlist via Store Adapter."""
        wl = await self.adapter.get_wishlist(wishlist_id)
        return wl.model_dump()

    async def add_to_wishlist(
        self, wishlist_id: str, product_id: str, variant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add item to wishlist via Store Adapter."""
        wl = await self.adapter.add_to_wishlist(wishlist_id, product_id, variant_id)
        return wl.model_dump()

    async def remove_from_wishlist(self, wishlist_id: str, item_id: str) -> Dict[str, Any]:
        """Remove item from wishlist via Store Adapter."""
        wl = await self.adapter.remove_from_wishlist(wishlist_id, item_id)
        return wl.model_dump()


store_client = StoreAPIClient()
