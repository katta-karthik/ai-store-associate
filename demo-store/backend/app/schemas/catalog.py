"""Pydantic V2 Schemas for Catalog & Cart API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VariantSchema(BaseModel):
    """Schema for Product Variant."""
    id: str
    size: Optional[str] = None
    color: Optional[str] = None
    price: float
    stock: int
    sku: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategorySchema(BaseModel):
    """Schema for Product Category."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    """Schema for Product Item."""
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
    variants: List[VariantSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Envelope response for product search/filter."""
    total: int
    items: List[ProductSchema]
    facets: Dict[str, Any] = Field(default_factory=dict)


class CartItemCreateSchema(BaseModel):
    """Schema to add/update item in cart."""
    product_id: str
    variant_id: str
    quantity: int = Field(default=1, ge=1, le=10)


class CartItemSchema(BaseModel):
    """Schema for line item in cart response."""
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


class CartSchema(BaseModel):
    """Schema for cart envelope response."""
    cart_id: str
    items: List[CartItemSchema] = Field(default_factory=list)
    subtotal: float = 0.0
    currency: str = "INR"
    item_count: int = 0


class StandardResponse(BaseModel):
    """Standardized API JSON Envelope."""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
