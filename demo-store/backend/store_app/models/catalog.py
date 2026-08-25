"""SQLAlchemy Database Models for E-Commerce Catalog & Cart."""

import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from store_app.core.database import Base


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Category(Base):
    """Product Category Model."""
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    """Product Catalog Model."""
    __tablename__ = "products"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    brand = Column(String(100), index=True, nullable=False)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=False)
    base_price = Column(Float, nullable=False, index=True)
    currency = Column(String(10), default="INR")
    rating = Column(Float, default=5.0)
    review_count = Column(Integer, default=0)
    primary_image = Column(String(500), nullable=False)
    images_json = Column(Text, default="[]")
    tags_json = Column(Text, default="[]")
    specs_json = Column(Text, default="{}")

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", lazy="selectin")


class ProductVariant(Base):
    """Product Variant (Size, Color, Stock) Model."""
    __tablename__ = "product_variants"

    id = Column(String(50), primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    size = Column(String(20), nullable=True, index=True)
    color = Column(String(50), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    sku = Column(String(50), nullable=True)

    product = relationship("Product", back_populates="variants")


class Cart(Base):
    """Shopper Cart Session Model."""
    __tablename__ = "carts"

    id = Column(String(100), primary_key=True, index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan", lazy="selectin")


class CartItem(Base):
    """Cart Line Item Model."""
    __tablename__ = "cart_items"

    id = Column(String(100), primary_key=True, index=True)
    cart_id = Column(String(100), ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    variant_id = Column(String(50), ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", lazy="selectin")
    variant = relationship("ProductVariant", lazy="selectin")
