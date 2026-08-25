"""Universal Commerce Store Adapter SDK Interface.

Defines the contract that any e-commerce provider (Shopify, WooCommerce,
BigCommerce, custom Next.js/FastAPI stores) implements to connect to ShopAgent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProductVariantDTO(BaseModel):
    """Data transfer object for product variant."""
    id: str
    size: Optional[str] = None
    color: Optional[str] = None
    price: float
    stock: int
    sku: Optional[str] = None


class ProductDTO(BaseModel):
    """Data transfer object for standardized product catalog."""
    id: str
    title: str
    brand: str
    category: str
    description: str
    base_price: float
    currency: str = "INR"
    rating: float = 5.0
    review_count: int = 0
    primary_image: str
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    specs: Dict[str, Any] = Field(default_factory=dict)
    variants: List[ProductVariantDTO] = Field(default_factory=list)


class CartItemDTO(BaseModel):
    """Data transfer object for a single line item in the cart."""
    item_id: str
    product_id: str
    variant_id: str
    title: str
    size: Optional[str] = None
    color: Optional[str] = None
    unit_price: float
    quantity: int
    total_price: float
    image: Optional[str] = None


class CartDTO(BaseModel):
    """Data transfer object for the shopping cart."""
    cart_id: str
    items: List[CartItemDTO] = Field(default_factory=list)
    subtotal: float = 0.0
    currency: str = "INR"
    item_count: int = 0


class WishlistItemDTO(BaseModel):
    """Data transfer object for a wishlist item."""
    item_id: str
    product_id: str
    variant_id: Optional[str] = None
    title: str
    brand: str
    price: float
    size: Optional[str] = None
    image: Optional[str] = None


class WishlistDTO(BaseModel):
    """Data transfer object for the wishlist."""
    wishlist_id: str
    items: List[WishlistItemDTO] = Field(default_factory=list)
    item_count: int = 0


class ProductSearchParams(BaseModel):
    """Standardized search and filter parameters."""
    query: Optional[str] = None
    category_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    in_stock: bool = True
    limit: int = 20
    offset: int = 0


class ProductSearchResultDTO(BaseModel):
    """Standardized search response with items and active facet counts."""
    total: int
    items: List[ProductDTO]
    facets: Dict[str, Any] = Field(default_factory=dict)


class UniversalStoreAdapter(ABC):
    """Abstract Base Class for Universal E-Commerce Store Adapters."""

    @abstractmethod
    async def search_products(self, params: ProductSearchParams) -> ProductSearchResultDTO:
        """Search and filter products across the merchant catalog."""
        pass

    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[ProductDTO]:
        """Fetch detailed product specifications and variant inventory."""
        pass

    @abstractmethod
    async def get_cart(self, cart_id: str) -> CartDTO:
        """Retrieve the active shopper cart."""
        pass

    @abstractmethod
    async def add_to_cart(
        self, cart_id: str, product_id: str, variant_id: str, quantity: int = 1
    ) -> CartDTO:
        """Add an item to the cart with inventory stock validation."""
        pass

    @abstractmethod
    async def remove_from_cart(self, cart_id: str, item_id: str) -> CartDTO:
        """Remove a line item from the active cart."""
        pass

    @abstractmethod
    async def get_wishlist(self, wishlist_id: str) -> WishlistDTO:
        """Retrieve the active shopper wishlist."""
        pass

    @abstractmethod
    async def add_to_wishlist(
        self, wishlist_id: str, product_id: str, variant_id: Optional[str] = None
    ) -> WishlistDTO:
        """Add a product or variant to the wishlist."""
        pass

    @abstractmethod
    async def remove_from_wishlist(self, wishlist_id: str, item_id: str) -> WishlistDTO:
        """Remove an item from the active wishlist."""
        pass

    @abstractmethod
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Retrieve all active product categories and sub-categories."""
        pass
