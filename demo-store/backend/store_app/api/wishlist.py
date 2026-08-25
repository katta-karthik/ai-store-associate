"""Wishlist & Saved-For-Later API Router."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from store_app.core.database import get_db
from store_app.models.catalog import Product, ProductVariant, Wishlist, WishlistItem
from store_app.schemas.catalog import (
    StandardResponse,
    WishlistItemCreateSchema,
    WishlistItemSchema,
    WishlistSchema,
)

router = APIRouter(prefix="/wishlist", tags=["Wishlist & Saved Items"])


async def get_or_create_wishlist(wishlist_id: str, db: AsyncSession) -> Wishlist:
    stmt = select(Wishlist).where(Wishlist.id == wishlist_id)
    res = await db.execute(stmt)
    wishlist = res.scalar_one_or_none()
    if not wishlist:
        wishlist = Wishlist(id=wishlist_id)
        db.add(wishlist)
        await db.commit()
        await db.refresh(wishlist)
    return wishlist


def format_wishlist_response(wishlist: Wishlist) -> WishlistSchema:
    items_out = []
    for it in wishlist.items:
        items_out.append(
            WishlistItemSchema(
                item_id=it.id,
                product_id=it.product_id,
                variant_id=it.variant_id,
                title=it.product.title if it.product else "Unknown Product",
                brand=it.product.brand if it.product else "Unknown",
                price=it.variant.price if (it.variant and it.variant.price) else (it.product.base_price if it.product else 0.0),
                size=it.variant.size if it.variant else None,
                image=it.product.primary_image if it.product else None,
            )
        )
    return WishlistSchema(
        wishlist_id=wishlist.id,
        items=items_out,
        item_count=len(items_out),
    )


@router.get("/{wishlist_id}", response_model=StandardResponse)
async def get_wishlist(wishlist_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch current items in a shopper's wishlist."""
    wishlist = await get_or_create_wishlist(wishlist_id, db)
    return StandardResponse(success=True, data=format_wishlist_response(wishlist))


@router.post("/{wishlist_id}/items", response_model=StandardResponse)
async def add_item_to_wishlist(
    wishlist_id: str,
    payload: WishlistItemCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Add a product or specific variant to the wishlist."""
    wishlist = await get_or_create_wishlist(wishlist_id, db)

    # Validate product exists
    prod_stmt = select(Product).where(Product.id == payload.product_id)
    prod_res = await db.execute(prod_stmt)
    product = prod_res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already in wishlist
    for it in wishlist.items:
        if it.product_id == payload.product_id and it.variant_id == payload.variant_id:
            return StandardResponse(success=True, data=format_wishlist_response(wishlist))

    item = WishlistItem(
        id=f"witem_{uuid.uuid4().hex[:12]}",
        wishlist_id=wishlist.id,
        product_id=payload.product_id,
        variant_id=payload.variant_id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(wishlist)

    return StandardResponse(success=True, data=format_wishlist_response(wishlist))


@router.delete("/{wishlist_id}/items/{item_id}", response_model=StandardResponse)
async def remove_item_from_wishlist(
    wishlist_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove an item from the wishlist."""
    stmt = select(WishlistItem).where(
        WishlistItem.id == item_id,
        WishlistItem.wishlist_id == wishlist_id,
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    await db.delete(item)
    await db.commit()

    wishlist = await get_or_create_wishlist(wishlist_id, db)
    return StandardResponse(success=True, data=format_wishlist_response(wishlist))
