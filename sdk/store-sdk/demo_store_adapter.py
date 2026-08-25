"""Demo Store REST Adapter implementation.

Connects to any standard REST e-commerce backend implementing the Universal Commerce API.
"""

from typing import Any, Dict, List, Optional
import httpx
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


class DemoStoreAdapter(UniversalStoreAdapter):
    """REST Client Adapter for Demo Store and Custom Commerce APIs."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1", timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search_products(self, params: ProductSearchParams) -> ProductSearchResultDTO:
        """Query REST store catalog with filters."""
        query_params: Dict[str, Any] = {"in_stock": params.in_stock, "limit": params.limit, "offset": params.offset}
        if params.query:
            query_params["q"] = params.query
        if params.category_id:
            query_params["category_id"] = params.category_id
        if params.min_price is not None:
            query_params["min_price"] = params.min_price
        if params.max_price is not None:
            query_params["max_price"] = params.max_price
        if params.brand:
            query_params["brand"] = params.brand
        if params.size:
            query_params["size"] = params.size

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/products", params=query_params)
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    items_raw = data.get("items", [])
                    total = data.get("total", len(items_raw))
                    facets = data.get("facets", {})

                    items: List[ProductDTO] = []
                    for it in items_raw:
                        variants = [
                            ProductVariantDTO(
                                id=v["id"],
                                size=v.get("size"),
                                color=v.get("color"),
                                price=float(v.get("price", 0.0)),
                                stock=int(v.get("stock", 0)),
                                sku=v.get("sku"),
                            )
                            for v in it.get("variants", [])
                        ]
                        items.append(
                            ProductDTO(
                                id=it["id"],
                                title=it["title"],
                                brand=it["brand"],
                                category=it.get("category", "General"),
                                description=it.get("description", ""),
                                base_price=float(it.get("base_price", 0.0)),
                                currency=it.get("currency", "INR"),
                                rating=float(it.get("rating", 5.0)),
                                review_count=int(it.get("review_count", 0)),
                                primary_image=it.get("primary_image", ""),
                                images=it.get("images", []),
                                tags=it.get("tags", []),
                                specs=it.get("specs", {}),
                                variants=variants,
                            )
                        )
                    return ProductSearchResultDTO(total=total, items=items, facets=facets)
                return ProductSearchResultDTO(total=0, items=[], facets={})
        except Exception:
            return ProductSearchResultDTO(total=0, items=[], facets={})

    async def get_product_by_id(self, product_id: str) -> Optional[ProductDTO]:
        """Fetch single product details by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/products/{product_id}")
                if res.status_code == 200:
                    it = res.json().get("data")
                    if not it:
                        return None
                    variants = [
                        ProductVariantDTO(
                            id=v["id"],
                            size=v.get("size"),
                            color=v.get("color"),
                            price=float(v.get("price", 0.0)),
                            stock=int(v.get("stock", 0)),
                            sku=v.get("sku"),
                        )
                        for v in it.get("variants", [])
                    ]
                    return ProductDTO(
                        id=it["id"],
                        title=it["title"],
                        brand=it["brand"],
                        category=it.get("category", "General"),
                        description=it.get("description", ""),
                        base_price=float(it.get("base_price", 0.0)),
                        currency=it.get("currency", "INR"),
                        rating=float(it.get("rating", 5.0)),
                        review_count=int(it.get("review_count", 0)),
                        primary_image=it.get("primary_image", ""),
                        images=it.get("images", []),
                        tags=it.get("tags", []),
                        specs=it.get("specs", {}),
                        variants=variants,
                    )
                return None
        except Exception:
            return None

    async def get_cart(self, cart_id: str) -> CartDTO:
        """Fetch active cart by session ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/cart/{cart_id}")
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    items = [
                        CartItemDTO(
                            item_id=i["item_id"],
                            product_id=i["product_id"],
                            variant_id=i["variant_id"],
                            title=i["title"],
                            size=i.get("size"),
                            color=i.get("color"),
                            unit_price=float(i.get("unit_price", 0.0)),
                            quantity=int(i.get("quantity", 1)),
                            total_price=float(i.get("total_price", 0.0)),
                            image=i.get("image"),
                        )
                        for i in data.get("items", [])
                    ]
                    return CartDTO(
                        cart_id=cart_id,
                        items=items,
                        subtotal=float(data.get("subtotal", 0.0)),
                        currency=data.get("currency", "INR"),
                        item_count=int(data.get("item_count", len(items))),
                    )
                return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)
        except Exception:
            return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> CartDTO:
        """Add item to cart via REST API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/cart/{cart_id}/items",
                    json={"product_id": product_id, "variant_id": variant_id, "quantity": quantity},
                )
                if res.status_code == 200:
                    return await self.get_cart(cart_id)
                return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)
        except Exception:
            return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def remove_from_cart(self, cart_id: str, item_id: str) -> CartDTO:
        """Remove line item from cart."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.delete(f"{self.base_url}/cart/{cart_id}/items/{item_id}")
                if res.status_code == 200:
                    return await self.get_cart(cart_id)
                return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)
        except Exception:
            return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def get_wishlist(self, wishlist_id: str) -> WishlistDTO:
        """Fetch active wishlist."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/wishlist/{wishlist_id}")
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    items = [
                        WishlistItemDTO(
                            item_id=i["item_id"],
                            product_id=i["product_id"],
                            variant_id=i.get("variant_id"),
                            title=i["title"],
                            brand=i.get("brand", "General"),
                            price=float(i.get("price", 0.0)),
                            size=i.get("size"),
                            image=i.get("image"),
                        )
                        for i in data.get("items", [])
                    ]
                    return WishlistDTO(
                        wishlist_id=wishlist_id,
                        items=items,
                        item_count=int(data.get("item_count", len(items))),
                    )
                return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)
        except Exception:
            return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)

    async def add_to_wishlist(
        self, wishlist_id: str, product_id: str, variant_id: Optional[str] = None
    ) -> WishlistDTO:
        """Add product to wishlist."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/wishlist/{wishlist_id}/items",
                    json={"product_id": product_id, "variant_id": variant_id},
                )
                if res.status_code == 200:
                    return await self.get_wishlist(wishlist_id)
                return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)
        except Exception:
            return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)

    async def remove_from_wishlist(self, wishlist_id: str, item_id: str) -> WishlistDTO:
        """Remove item from wishlist."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.delete(f"{self.base_url}/wishlist/{wishlist_id}/items/{item_id}")
                if res.status_code == 200:
                    return await self.get_wishlist(wishlist_id)
                return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)
        except Exception:
            return WishlistDTO(wishlist_id=wishlist_id, items=[], item_count=0)

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Fetch categories."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.base_url}/categories")
                if res.status_code == 200:
                    return res.json().get("data", [])
                return []
        except Exception:
            return []
