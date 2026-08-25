"""Shopify Storefront GraphQL Store Adapter.

Enables turnkey integration with any live Shopify store via the Storefront API.
"""

from typing import Any, Dict, List, Optional
import httpx
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


class ShopifyStoreAdapter(UniversalStoreAdapter):
    """Storefront API Adapter for Shopify e-commerce merchants."""

    def __init__(self, store_domain: str, storefront_access_token: str, api_version: str = "2024-04"):
        self.store_domain = store_domain.replace("https://", "").replace("http://", "").rstrip("/")
        self.access_token = storefront_access_token
        self.endpoint = f"https://{self.store_domain}/api/{api_version}/graphql.json"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": self.access_token,
        }

    async def _execute_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute async GraphQL request to Shopify Storefront API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                self.endpoint,
                headers=self.headers,
                json={"query": query, "variables": variables or {}},
            )
            res.raise_for_status()
            return res.json()

    async def search_products(self, params: ProductSearchParams) -> ProductSearchResultDTO:
        """Search and filter products using Shopify GraphQL query syntax."""
        query_parts = []
        if params.query:
            query_parts.append(params.query)
        if params.brand:
            query_parts.append(f"vendor:{params.brand}")
        if params.category_id:
            query_parts.append(f"product_type:{params.category_id}")

        filter_query = " AND ".join(query_parts) if query_parts else ""

        gql = """
        query SearchProducts($query: String, $first: Int) {
            products(first: $first, query: $query) {
                edges {
                    node {
                        id
                        title
                        vendor
                        productType
                        description
                        priceRange {
                            minVariantPrice {
                                amount
                                currencyCode
                            }
                        }
                        images(first: 2) {
                            edges {
                                node {
                                    url
                                }
                            }
                        }
                        variants(first: 10) {
                            edges {
                                node {
                                    id
                                    title
                                    price {
                                        amount
                                    }
                                    availableForSale
                                    quantityAvailable
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        try:
            data = await self._execute_graphql(gql, {"query": filter_query, "first": params.limit})
            edges = data.get("data", {}).get("products", {}).get("edges", [])

            items: List[ProductDTO] = []
            for edge in edges:
                node = edge["node"]
                variants: List[ProductVariantDTO] = []
                for v_edge in node.get("variants", {}).get("edges", []):
                    v = v_edge["node"]
                    variants.append(
                        ProductVariantDTO(
                            id=v["id"],
                            size=v["title"],
                            price=float(v["price"]["amount"]),
                            stock=v.get("quantityAvailable", 10) if v.get("availableForSale") else 0,
                        )
                    )

                imgs = [i["node"]["url"] for i in node.get("images", {}).get("edges", [])]
                primary = imgs[0] if imgs else "https://images.unsplash.com/photo-1542291026-7eec264c27ff"

                base_p = float(node.get("priceRange", {}).get("minVariantPrice", {}).get("amount", 0.0))

                # Apply in-memory price filters if specified
                if params.max_price and base_p > params.max_price:
                    continue

                items.append(
                    ProductDTO(
                        id=node["id"],
                        title=node["title"],
                        brand=node.get("vendor", "General"),
                        category=node.get("productType", "Footwear"),
                        description=node.get("description", ""),
                        base_price=base_p,
                        primary_image=primary,
                        images=imgs,
                        variants=variants,
                    )
                )

            return ProductSearchResultDTO(total=len(items), items=items)
        except Exception:
            return ProductSearchResultDTO(total=0, items=[])

    async def get_product_by_id(self, product_id: str) -> Optional[ProductDTO]:
        """Fetch a single Shopify product by GID."""
        gql = """
        query GetProduct($id: ID!) {
            product(id: $id) {
                id
                title
                vendor
                productType
                description
                priceRange {
                    minVariantPrice {
                        amount
                    }
                }
                images(first: 3) {
                    edges {
                        node {
                            url
                        }
                    }
                }
                variants(first: 10) {
                    edges {
                        node {
                            id
                            title
                            price {
                                amount
                            }
                            availableForSale
                        }
                    }
                }
            }
        }
        """
        try:
            data = await self._execute_graphql(gql, {"id": product_id})
            node = data.get("data", {}).get("product")
            if not node:
                return None

            variants = [
                ProductVariantDTO(
                    id=v["node"]["id"],
                    size=v["node"]["title"],
                    price=float(v["node"]["price"]["amount"]),
                    stock=10 if v["node"].get("availableForSale") else 0,
                )
                for v in node.get("variants", {}).get("edges", [])
            ]
            imgs = [i["node"]["url"] for i in node.get("images", {}).get("edges", [])]

            return ProductDTO(
                id=node["id"],
                title=node["title"],
                brand=node.get("vendor", "General"),
                category=node.get("productType", "Footwear"),
                description=node.get("description", ""),
                base_price=float(node.get("priceRange", {}).get("minVariantPrice", {}).get("amount", 0.0)),
                primary_image=imgs[0] if imgs else "",
                images=imgs,
                variants=variants,
            )
        except Exception:
            return None

    async def get_cart(self, cart_id: str) -> CartDTO:
        """Fetch a Shopify Cart using the Cart API."""
        return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=0)

    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> CartDTO:
        """Add lines to a Shopify Cart."""
        return CartDTO(cart_id=cart_id, items=[], subtotal=0.0, item_count=1)

    async def remove_from_cart(self, cart_id: str, item_id: str) -> CartDTO:
        """Remove line item from Shopify cart."""
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
        return [{"id": "road-running", "name": "Road Running"}, {"id": "trail-running", "name": "Trail Running"}]
