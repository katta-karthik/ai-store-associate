"""Store Tool Handlers interacting with the Universal Commerce API."""

from typing import Any, Dict, List, Optional
import httpx
from agent_app.core.config import settings
from agent_app.schemas.agent_state import ExtractedFilters


class StoreAPIClient:
    """HTTP Client connecting to the Universal Commerce API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.STORE_API_URL).rstrip("/")

    async def search_products(self, filters: ExtractedFilters) -> Dict[str, Any]:
        """Call GET /api/v1/products with extracted filter parameters."""
        params: Dict[str, Any] = {"in_stock": True}
        if filters.query:
            params["q"] = filters.query
        if filters.category_id:
            params["category_id"] = filters.category_id
        if filters.min_price is not None:
            params["min_price"] = filters.min_price
        if filters.max_price is not None:
            params["max_price"] = filters.max_price
        if filters.brand:
            params["brand"] = filters.brand
        if filters.size:
            params["size"] = filters.size

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/products", params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("data", {"total": 0, "items": []})
                return {"total": 0, "items": [], "error": f"Store API returned status {resp.status_code}"}
        except Exception as e:
            return {"total": 0, "items": [], "error": str(e)}

    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Call GET /api/v1/products/{id}."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/products/{product_id}")
                if resp.status_code == 200:
                    return resp.json().get("data")
                return None
        except Exception:
            return None

    # Cart Tools
    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        """Fetch active cart."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/cart/{cart_id}")
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {"cart_id": cart_id, "items": [], "item_count": 0, "subtotal": 0.0}
        except Exception as e:
            return {"cart_id": cart_id, "items": [], "item_count": 0, "subtotal": 0.0, "error": str(e)}

    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> Dict[str, Any]:
        """Add item to cart."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.base_url}/cart/{cart_id}/items",
                    json={"product_id": product_id, "variant_id": variant_id, "quantity": quantity},
                )
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def remove_from_cart(self, cart_id: str, item_id: str) -> Dict[str, Any]:
        """Remove item from cart."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.delete(f"{self.base_url}/cart/{cart_id}/items/{item_id}")
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    # Wishlist Tools
    async def get_wishlist(self, wishlist_id: str) -> Dict[str, Any]:
        """Fetch active wishlist."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/wishlist/{wishlist_id}")
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {"wishlist_id": wishlist_id, "items": [], "item_count": 0}
        except Exception as e:
            return {"wishlist_id": wishlist_id, "items": [], "item_count": 0, "error": str(e)}

    async def add_to_wishlist(
        self, wishlist_id: str, product_id: str, variant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add item to wishlist."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.base_url}/wishlist/{wishlist_id}/items",
                    json={"product_id": product_id, "variant_id": variant_id},
                )
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}


store_client = StoreAPIClient()
