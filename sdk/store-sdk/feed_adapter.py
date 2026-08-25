"""Product Catalog Feed Ingestion Adapter.

Allows any custom e-commerce store (Spring Boot, MERN, Django, PHP/Laravel, Magento)
to connect to ShopAgent with ZERO backend changes by simply providing a Product Catalog Feed URL.
"""

from typing import Any, Dict, List, Optional
import httpx
import time

try:
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
except ImportError:
    from universal_adapter import (
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


class CatalogFeedAdapter(UniversalStoreAdapter):
    """Universal Store Adapter consuming JSON/REST Product Feeds."""

    def __init__(self, feed_url: str, cache_ttl_seconds: int = 3600):
        self.feed_url = feed_url
        self.cache_ttl = cache_ttl_seconds
        self._cached_products: List[ProductDTO] = []
        self._last_fetched_at: float = 0.0

    async def _ensure_catalog_synced(self) -> List[ProductDTO]:
        """Fetch and refresh product catalog from feed URL if cache expired."""
        now = time.time()
        if self._cached_products and (now - self._last_fetched_at) < self.cache_ttl:
            return self._cached_products

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(self.feed_url)
                if res.status_code == 200:
                    raw_data = res.json()
                    # Handle array or { products: [...] } or { items: [...] }
                    items_list = raw_data if isinstance(raw_data, list) else (
                        raw_data.get("products") or raw_data.get("items") or raw_data.get("data", {}).get("items", [])
                    )

                    products: List[ProductDTO] = []
                    for it in items_list:
                        variants = [
                            ProductVariantDTO(
                                id=v.get("id", f"{it.get('id', 'item')}_{v.get('size', idx)}"),
                                size=str(v.get("size", "Standard")),
                                color=v.get("color"),
                                price=float(v.get("price", it.get("price", it.get("base_price", 0.0)))),
                                stock=int(v.get("stock", v.get("inventory_quantity", 10))),
                                sku=v.get("sku"),
                            )
                            for idx, v in enumerate(it.get("variants", []))
                        ]
                        if not variants:
                            # Create default variant if none provided
                            variants = [
                                ProductVariantDTO(
                                    id=f"{it.get('id', 'item')}_def",
                                    size="Standard",
                                    price=float(it.get("price", it.get("base_price", 0.0))),
                                    stock=10,
                                )
                            ]

                        imgs = it.get("images", [])
                        primary = it.get("primary_image") or (imgs[0] if imgs else "https://images.unsplash.com/photo-1542291026-7eec264c27ff")

                        products.append(
                            ProductDTO(
                                id=str(it.get("id")),
                                title=it.get("title", it.get("name", "")),
                                brand=it.get("brand", it.get("vendor", "General")),
                                category=it.get("category", it.get("product_type", "General")),
                                description=it.get("description", ""),
                                base_price=float(it.get("base_price", it.get("price", 0.0))),
                                currency=it.get("currency", "INR"),
                                rating=float(it.get("rating", 5.0)),
                                review_count=int(it.get("review_count", 0)),
                                primary_image=primary,
                                images=imgs if isinstance(imgs, list) else [primary],
                                tags=it.get("tags", []),
                                specs=it.get("specs", {}),
                                variants=variants,
                            )
                        )
                    self._cached_products = products
                    self._last_fetched_at = now
        except Exception:
            pass

        return self._cached_products

    async def search_products(self, params: ProductSearchParams) -> ProductSearchResultDTO:
        """Search products from the synchronized feed with filtering."""
        products = await self._ensure_catalog_synced()
        filtered = products

        if params.query:
            q = params.query.lower()
            filtered = [
                p for p in filtered
                if q in p.title.lower() or q in p.brand.lower() or q in p.description.lower() or any(q in t.lower() for t in p.tags)
            ]

        if params.brand:
            b = params.brand.lower()
            filtered = [p for p in filtered if b in p.brand.lower()]

        if params.category_id:
            c = params.category_id.lower()
            filtered = [p for p in filtered if c in p.category.lower()]

        if params.min_price is not None:
            filtered = [p for p in filtered if p.base_price >= params.min_price]

        if params.max_price is not None:
            filtered = [p for p in filtered if p.base_price <= params.max_price]

        if params.size:
            s = str(params.size).lower()
            filtered = [
                p for p in filtered
                if any(v.size and s in v.size.lower() for v in p.variants)
            ]

        total = len(filtered)
        paginated = filtered[params.offset : params.offset + params.limit]

        return ProductSearchResultDTO(total=total, items=paginated, facets={})

    async def get_product_by_id(self, product_id: str) -> Optional[ProductDTO]:
        """Lookup single product in catalog feed cache."""
        products = await self._ensure_catalog_synced()
        for p in products:
            if p.id == product_id:
                return p
        return None

    async def get_cart(self, cart_id: str) -> CartDTO:
        """Browser event bridge handles cart for feed stores; returns local session cart."""
        return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> CartDTO:
        """Cart is dispatched via frontend event bridge."""
        return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=1)

    async def remove_from_cart(self, cart_id: str, item_id: str) -> CartDTO:
        return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def get_wishlist(self, wishlist_id: str) -> WishlistDTO:
        return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)

    async def add_to_wishlist(
        self, wishlist_id: str, product_id: str, variant_id: Optional[str] = None
    ) -> WishlistDTO:
        return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=1)

    async def remove_from_wishlist(self, wishlist_id: str, item_id: str) -> WishlistDTO:
        return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)

    async def get_categories(self) -> List[Dict[str, Any]]:
        products = await self._ensure_catalog_synced()
        cats = set(p.category for p in products if p.category)
        return [{"id": c.lower().replace(" ", "-"), "name": c} for c in cats]
