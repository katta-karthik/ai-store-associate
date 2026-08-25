"""Realistic E-Commerce Seed Catalog for Demo Store."""

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog import Category, Product, ProductVariant

CATEGORIES_DATA = [
    {
        "id": "cat_running",
        "name": "Running Shoes",
        "slug": "running-shoes",
        "description": "Engineered road and daily training running shoes."
    },
    {
        "id": "cat_trail",
        "name": "Trail & Outdoor",
        "slug": "trail-outdoor",
        "description": "Durable, high-traction footwear for trail running and hiking."
    },
    {
        "id": "cat_sneakers",
        "name": "Lifestyle & Sneakers",
        "slug": "lifestyle-sneakers",
        "description": "Comfortable street-style sneakers for daily wear."
    }
]

PRODUCTS_DATA = [
    {
        "id": "prod_nike_pegasus_41",
        "title": "Nike Air Zoom Pegasus 41",
        "brand": "Nike",
        "category_id": "cat_running",
        "description": "Responsive cushioning in the Pegasus provides an energized ride for daily road runs. Features dual Air Zoom units and a lightweight engineered mesh upper.",
        "base_price": 7899.0,
        "currency": "INR",
        "rating": 4.8,
        "review_count": 342,
        "primary_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
        "images": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600"
        ],
        "tags": ["running", "road", "lightweight", "cushioned", "neutral"],
        "specs": {
            "weight_grams": 281,
            "heel_drop_mm": 10,
            "surface": "Road",
            "support_type": "Neutral",
            "cushioning": "Responsive"
        },
        "variants": [
            {"id": "var_peg_blk_8", "size": "8", "color": "Black/White", "price": 7899.0, "stock": 10, "sku": "NK-PEG41-BLK-8"},
            {"id": "var_peg_blk_9", "size": "9", "color": "Black/White", "price": 7899.0, "stock": 14, "sku": "NK-PEG41-BLK-9"},
            {"id": "var_peg_blk_10", "size": "10", "color": "Black/White", "price": 7899.0, "stock": 8, "sku": "NK-PEG41-BLK-10"},
            {"id": "var_peg_blk_11", "size": "11", "color": "Black/White", "price": 7899.0, "stock": 5, "sku": "NK-PEG41-BLK-11"}
        ]
    },
    {
        "id": "prod_adidas_ultraboost_light",
        "title": "Adidas Ultraboost Light",
        "brand": "Adidas",
        "category_id": "cat_running",
        "description": "Experience epic energy with the Ultraboost Light. Featuring 30% lighter BOOST material and a Continental rubber outsole for maximum grip.",
        "base_price": 7499.0,
        "currency": "INR",
        "rating": 4.7,
        "review_count": 289,
        "primary_image": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600",
        "images": [
            "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600"
        ],
        "tags": ["running", "road", "boost", "energy-return", "plush"],
        "specs": {
            "weight_grams": 293,
            "heel_drop_mm": 10,
            "surface": "Road",
            "support_type": "Neutral",
            "cushioning": "Max"
        },
        "variants": [
            {"id": "var_ub_wht_8", "size": "8", "color": "Cloud White", "price": 7499.0, "stock": 12, "sku": "AD-UB-WHT-8"},
            {"id": "var_ub_wht_9", "size": "9", "color": "Cloud White", "price": 7499.0, "stock": 9, "sku": "AD-UB-WHT-9"},
            {"id": "var_ub_wht_10", "size": "10", "color": "Cloud White", "price": 7499.0, "stock": 0, "sku": "AD-UB-WHT-10"},
            {"id": "var_ub_wht_11", "size": "11", "color": "Cloud White", "price": 7499.0, "stock": 4, "sku": "AD-UB-WHT-11"}
        ]
    },
    {
        "id": "prod_puma_velocity_nitro_3",
        "title": "Puma Velocity Nitro 3",
        "brand": "Puma",
        "category_id": "cat_running",
        "description": "An all-in-one daily runner with NITROFOAM technology for lightweight responsiveness and PUMAGRIP durable rubber.",
        "base_price": 6299.0,
        "currency": "INR",
        "rating": 4.6,
        "review_count": 180,
        "primary_image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600",
        "images": [
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600"
        ],
        "tags": ["running", "road", "budget-friendly", "nitro", "lightweight"],
        "specs": {
            "weight_grams": 264,
            "heel_drop_mm": 8,
            "surface": "Road",
            "support_type": "Neutral",
            "cushioning": "Balanced"
        },
        "variants": [
            {"id": "var_pum_blu_9", "size": "9", "color": "Electric Blue", "price": 6299.0, "stock": 16, "sku": "PM-VN3-BLU-9"},
            {"id": "var_pum_blu_10", "size": "10", "color": "Electric Blue", "price": 6299.0, "stock": 11, "sku": "PM-VN3-BLU-10"}
        ]
    },
    {
        "id": "prod_salomon_speedcross_6",
        "title": "Salomon Speedcross 6 Gore-Tex",
        "brand": "Salomon",
        "category_id": "cat_trail",
        "description": "Legendary grip and waterproof protection for muddy trails and rugged technical terrain. Quicklace system with Sensifit construction.",
        "base_price": 11499.0,
        "currency": "INR",
        "rating": 4.9,
        "review_count": 420,
        "primary_image": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=600",
        "images": [
            "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=600"
        ],
        "tags": ["trail", "waterproof", "gore-tex", "aggressive-grip", "mud"],
        "specs": {
            "weight_grams": 328,
            "heel_drop_mm": 10,
            "surface": "Trail / Mud / Snow",
            "support_type": "Stability",
            "cushioning": "Protective"
        },
        "variants": [
            {"id": "var_sal_blk_9", "size": "9", "color": "Black/Phantom", "price": 11499.0, "stock": 7, "sku": "SAL-SC6-BLK-9"},
            {"id": "var_sal_blk_10", "size": "10", "color": "Black/Phantom", "price": 11499.0, "stock": 6, "sku": "SAL-SC6-BLK-10"}
        ]
    },
    {
        "id": "prod_nike_dunk_low_retro",
        "title": "Nike Dunk Low Retro",
        "brand": "Nike",
        "category_id": "cat_sneakers",
        "description": "Created for the hardwood but taken to the streets, the 80s b-ball icon returns with classic details and throwback hoops flair.",
        "base_price": 8295.0,
        "currency": "INR",
        "rating": 4.8,
        "review_count": 890,
        "primary_image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600",
        "images": [
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600"
        ],
        "tags": ["lifestyle", "streetwear", "casual", "panda", "retro"],
        "specs": {
            "weight_grams": 410,
            "heel_drop_mm": 0,
            "surface": "Casual",
            "support_type": "Standard",
            "cushioning": "Low"
        },
        "variants": [
            {"id": "var_dnk_pnd_8", "size": "8", "color": "White/Black Panda", "price": 8295.0, "stock": 3, "sku": "NK-DNK-PND-8"},
            {"id": "var_dnk_pnd_9", "size": "9", "color": "White/Black Panda", "price": 8295.0, "stock": 0, "sku": "NK-DNK-PND-9"},
            {"id": "var_dnk_pnd_10", "size": "10", "color": "White/Black Panda", "price": 8295.0, "stock": 4, "sku": "NK-DNK-PND-10"}
        ]
    }
]


async def seed_database(db: AsyncSession) -> None:
    """Populate database with initial categories, products, and variants."""
    cat_result = await db.execute(select(Category))
    if cat_result.scalars().first():
        return  # Already seeded

    # 1. Seed Categories
    for cat_data in CATEGORIES_DATA:
        category = Category(
            id=cat_data["id"],
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data["description"]
        )
        db.add(category)
    await db.flush()

    # 2. Seed Products and Variants
    for prod_data in PRODUCTS_DATA:
        product = Product(
            id=prod_data["id"],
            title=prod_data["title"],
            brand=prod_data["brand"],
            category_id=prod_data["category_id"],
            description=prod_data["description"],
            base_price=prod_data["base_price"],
            currency=prod_data["currency"],
            rating=prod_data["rating"],
            review_count=prod_data["review_count"],
            primary_image=prod_data["primary_image"],
            images_json=json.dumps(prod_data["images"]),
            tags_json=json.dumps(prod_data["tags"]),
            specs_json=json.dumps(prod_data["specs"]),
        )
        db.add(product)
        await db.flush()

        for var_data in prod_data["variants"]:
            variant = ProductVariant(
                id=var_data["id"],
                product_id=product.id,
                size=var_data["size"],
                color=var_data["color"],
                price=var_data["price"],
                stock=var_data["stock"],
                sku=var_data["sku"],
            )
            db.add(variant)

    await db.commit()
