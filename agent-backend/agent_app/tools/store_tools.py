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


store_client = StoreAPIClient()
