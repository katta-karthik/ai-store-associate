"""Shopping Cart API Endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from store_app.core.database import get_db
from store_app.models.catalog import Cart, CartItem, Product, ProductVariant
from store_app.schemas.catalog import CartItemCreateSchema, CartItemSchema, CartSchema, StandardResponse

router = APIRouter(prefix="/cart", tags=["Cart"])


async def _get_or_create_cart(cart_id: str, db: AsyncSession) -> Cart:
    """Retrieve existing cart or create new cart session."""
    query = (
        select(Cart)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.items).selectinload(CartItem.variant),
        )
        .filter(Cart.id == cart_id)
    )
    result = await db.execute(query)
    cart = result.scalars().first()

    if not cart:
        cart = Cart(id=cart_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart


def _format_cart(cart: Cart) -> CartSchema:
    """Helper to format Cart model into Pydantic CartSchema."""
    items = []
    subtotal = 0.0
    item_count = 0

    for item in cart.items:
        if item.variant and item.product:
            line_total = item.variant.price * item.quantity
            subtotal += line_total
            item_count += item.quantity
            items.append(
                CartItemSchema(
                    item_id=item.id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    title=item.product.title,
                    size=item.variant.size,
                    color=item.variant.color,
                    unit_price=item.variant.price,
                    quantity=item.quantity,
                    total_price=line_total,
                    image=item.product.primary_image,
                )
            )

    return CartSchema(
        cart_id=cart.id,
        items=items,
        subtotal=round(subtotal, 2),
        currency="INR",
        item_count=item_count,
    )


@router.get("/{cart_id}", response_model=StandardResponse)
async def get_cart(cart_id: str, db: AsyncSession = Depends(get_db)) -> StandardResponse:
    """Fetch current active cart details and subtotal."""
    cart = await _get_or_create_cart(cart_id, db)
    return StandardResponse(success=True, data=_format_cart(cart).model_dump())


@router.post("/{cart_id}/items", response_model=StandardResponse)
async def add_item_to_cart(
    cart_id: str,
    payload: CartItemCreateSchema,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    """Add or increment an item in the cart with inventory stock validation."""
    cart = await _get_or_create_cart(cart_id, db)

    # 1. Verify product and variant existence & stock
    var_query = (
        select(ProductVariant)
        .options(selectinload(ProductVariant.product))
        .filter(
            ProductVariant.id == payload.variant_id,
            ProductVariant.product_id == payload.product_id,
        )
    )
    var_res = await db.execute(var_query)
    variant = var_res.scalars().first()

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant '{payload.variant_id}' for Product '{payload.product_id}' not found.",
        )

    if variant.stock < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient inventory. Requested {payload.quantity}, but only {variant.stock} available in stock.",
        )

    # 2. Check if item already exists in cart
    existing_item = next(
        (i for i in cart.items if i.variant_id == payload.variant_id), None
    )

    if existing_item:
        new_qty = existing_item.quantity + payload.quantity
        if variant.stock < new_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add {payload.quantity} more. Total in cart ({new_qty}) exceeds available stock ({variant.stock}).",
            )
        existing_item.quantity = new_qty
    else:
        new_item = CartItem(
            id=f"item_{uuid.uuid4().hex[:12]}",
            cart_id=cart.id,
            product_id=payload.product_id,
            variant_id=payload.variant_id,
            quantity=payload.quantity,
        )
        db.add(new_item)

    await db.commit()
    db.expire_all()

    updated_cart = await _get_or_create_cart(cart_id, db)
    return StandardResponse(success=True, data=_format_cart(updated_cart).model_dump())


@router.delete("/{cart_id}/items/{item_id}", response_model=StandardResponse)
async def remove_item_from_cart(
    cart_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    """Remove a specific line item from the cart."""
    cart = await _get_or_create_cart(cart_id, db)
    item_to_remove = next((i for i in cart.items if i.id == item_id), None)

    if not item_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item '{item_id}' not found in cart '{cart_id}'.",
        )

    await db.delete(item_to_remove)
    await db.commit()
    db.expire_all()

    updated_cart = await _get_or_create_cart(cart_id, db)
    return StandardResponse(success=True, data=_format_cart(updated_cart).model_dump())
