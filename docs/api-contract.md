# 📑 Universal Commerce API & SSE Stream Contract (v1)

## 1. Catalog Endpoints

### 1.1 `GET /api/v1/products`
Query products with multi-dimensional filtering.

**Query Parameters:**
* `q` (string, optional): Full-text search term (e.g., "running shoes lightweight")
* `category_id` (string, optional): Category slug or ID
* `min_price` (float, optional): Lower price bound in store currency
* `max_price` (float, optional): Upper price bound
* `brand` (string, optional): Filter by brand
* `in_stock` (bool, default: `true`): Filter in-stock items
* `limit` (int, default: 20, max: 100): Pagination limit
* `offset` (int, default: 0): Pagination offset

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 45,
    "items": [
      {
        "id": "prod_pegasus_41",
        "title": "Nike Air Zoom Pegasus 41",
        "brand": "Nike",
        "category": "Running Shoes",
        "base_price": 7899.00,
        "currency": "INR",
        "rating": 4.8,
        "review_count": 312,
        "primary_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "tags": ["running", "road", "cushioned", "lightweight"],
        "variants": [
          { "id": "var_peg_blk_10", "size": "10", "color": "Black/White", "price": 7899.00, "stock": 15 },
          { "id": "var_peg_blk_9", "size": "9", "color": "Black/White", "price": 7899.00, "stock": 4 }
        ]
      }
    ],
    "facets": {
      "categories": [{"id": "running-shoes", "name": "Running Shoes", "count": 28}],
      "brands": [{"name": "Nike", "count": 14}, {"name": "Adidas", "count": 12}],
      "price_range": {"min": 3499.00, "max": 14999.00}
    }
  },
  "error": null
}
```

---

### 1.2 `GET /api/v1/products/{product_id}`
Retrieve complete detail, specifications, and full variant inventory for a product.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "prod_pegasus_41",
    "title": "Nike Air Zoom Pegasus 41",
    "brand": "Nike",
    "description": "Responsive cushioning in the Pegasus provides an energized ride for daily road runs.",
    "base_price": 7899.00,
    "currency": "INR",
    "specs": {
      "weight_grams": 281,
      "heel_drop_mm": 10,
      "surface": "Road",
      "support_type": "Neutral"
    },
    "variants": [
      { "id": "var_peg_blk_10", "size": "10", "color": "Black/White", "price": 7899.00, "stock": 15 }
    ]
  },
  "error": null
}
```

---

## 2. Cart & Commerce Endpoints

### 2.1 `GET /api/v1/cart/{cart_id}`
Retrieve the active shopper cart.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "cart_id": "cart_session_123",
    "items": [
      {
        "item_id": "item_abc_1",
        "product_id": "prod_pegasus_41",
        "variant_id": "var_peg_blk_10",
        "title": "Nike Air Zoom Pegasus 41",
        "size": "10",
        "color": "Black/White",
        "unit_price": 7899.00,
        "quantity": 1,
        "total_price": 7899.00,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
      }
    ],
    "subtotal": 7899.00,
    "currency": "INR",
    "item_count": 1
  },
  "error": null
}
```

### 2.2 `POST /api/v1/cart/{cart_id}/items`
Add or update an item in the cart with atomic inventory validation.

**Request Body:**
```json
{
  "product_id": "prod_pegasus_41",
  "variant_id": "var_peg_blk_10",
  "quantity": 1
}
```

---

## 3. Real-Time SSE Agent Streaming Protocol

### 3.1 Stream Event Types
When an active shopper sends a conversational query (`POST /api/v1/chat/stream`), the agent brain streams SSE frames:

1. **`token`**: Text streaming chunk
   ```
   data: {"event": "token", "content": "I found 3 great road running shoes "}
   ```
2. **`ui_action`**: Real-time browser control command
   ```
   data: {"event": "ui_action", "action": "SET_FILTERS", "payload": {"category": "running-shoes", "max_price": 8000, "size": "10"}}
   ```
3. **`cart_mutation`**: Commerce cart update
   ```
   data: {"event": "cart_mutation", "action": "ITEM_ADDED", "payload": {"product_title": "Nike Pegasus 41", "size": "10", "cart_count": 1}}
   ```
4. **`done`**: End of generation turn
   ```
   data: {"event": "done", "metadata": {"tokens_used": 340, "latency_ms": 1120}}
   ```
