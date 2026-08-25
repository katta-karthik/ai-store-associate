"""Product Catalog & Search API Endpoints."""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.catalog import Category, Product, ProductVariant
from app.schemas.catalog import CategorySchema, ProductListResponse, ProductSchema, StandardResponse, VariantSchema

router = APIRouter(prefix="/products", tags=["Products"])


def _format_product(product: Product) -> ProductSchema:
    """Helper to transform SQLAlchemy Product model to Pydantic ProductSchema."""
    variants = [
        VariantSchema(
            id=v.id,
            size=v.size,
            color=v.color,
            price=v.price,
            stock=v.stock,
            sku=v.sku,
        )
        for v in product.variants
    ]
    return ProductSchema(
        id=product.id,
        title=product.title,
        brand=product.brand,
        category=product.category.name if product.category else "",
        description=product.description,
        base_price=product.base_price,
        currency=product.currency,
        rating=product.rating,
        review_count=product.review_count,
        primary_image=product.primary_image,
        images=json.loads(product.images_json or "[]"),
        tags=json.loads(product.tags_json or "[]"),
        specs=json.loads(product.specs_json or "{}"),
        variants=variants,
    )


@router.get("", response_model=StandardResponse)
async def list_products(
    q: Optional[str] = Query(None, description="Full-text search query"),
    category_id: Optional[str] = Query(None, description="Filter by category ID or slug"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    size: Optional[str] = Query(None, description="Filter by shoe/clothing size"),
    in_stock: bool = Query(True, description="Only return items with available inventory"),
    limit: int = Query(20, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    """Search and filter products with dynamic facets."""
    query = select(Product).options(selectinload(Product.category), selectinload(Product.variants))

    # 1. Full-text search
    if q:
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_term),
                Product.description.ilike(search_term),
                Product.brand.ilike(search_term),
                Product.tags_json.ilike(search_term),
            )
        )

    # 2. Category filter
    if category_id:
        query = query.join(Product.category).filter(
            or_(Category.id == category_id, Category.slug == category_id)
        )

    # 3. Brand filter
    if brand:
        query = query.filter(Product.brand.ilike(brand.strip()))

    # 4. Price bounds
    if min_price is not None:
        query = query.filter(Product.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.base_price <= max_price)

    # 5. Size / Stock filter
    if size or in_stock:
        var_filter = []
        if size:
            var_filter.append(ProductVariant.size == size.strip())
        if in_stock:
            var_filter.append(ProductVariant.stock > 0)
        query = query.filter(Product.variants.any(*var_filter))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one_or_none() or 0

    # Paginate
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    formatted_items = [_format_product(p) for p in products]

    # Collect Facets
    facets: Dict[str, Any] = {
        "categories": [],
        "brands": [],
        "price_range": {"min": 0, "max": 0},
    }
    cat_res = await db.execute(select(Category))
    facets["categories"] = [{"id": c.id, "slug": c.slug, "name": c.name} for c in cat_res.scalars().all()]

    return StandardResponse(
        success=True,
        data=ProductListResponse(
            total=total_count,
            items=formatted_items,
            facets=facets,
        ).model_dump(),
    )


@router.get("/categories", response_model=StandardResponse)
async def list_categories(db: AsyncSession = Depends(get_db)) -> StandardResponse:
    """Retrieve all product categories."""
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return StandardResponse(
        success=True,
        data=[CategorySchema.model_validate(c).model_dump() for c in categories],
    )


@router.get("/{product_id}", response_model=StandardResponse)
async def get_product_details(
    product_id: str,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    """Get rich product detail specifications and variant stock."""
    query = (
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.variants))
        .filter(Product.id == product_id)
    )
    result = await db.execute(query)
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' was not found in the catalog.",
        )

    return StandardResponse(
        success=True,
        data=_format_product(product).model_dump(),
    )
