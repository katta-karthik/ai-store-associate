# 🏛️ System Architecture & Universal Integration RFC

## 1. System Vision & Core Decoupling
**ShopAgent** is designed as a universal, standalone AI Store Associate brain that connects to ANY e-commerce store regardless of whether the store is built with Shopify, WooCommerce, Magento, BigCommerce, or custom Next.js/FastAPI backends.

```
┌─────────────────────────────────────────────────────────────┐
│                 SHOPAGENT RUNTIME TOPOLOGY                  │
├──────────────────────────────┬──────────────────────────────┤
│    STOREFRONT CLIENT         │      AI ASSOCIATE BRAIN      │
│  Next.js / Shopify Theme     │  FastAPI + LangGraph Service │
│  Real-time SSE UI Listener   │  pgvector Semantic Memory    │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │
               │  REST (Tool Calls) & SSE     │
               ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 UNIVERSAL COMMERCE ADAPTER                  │
│       Standardized REST / Webhook Integration Layer         │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
      ┌───────────┐      ┌───────────┐      ┌───────────┐
      │  Shopify  │      │WooCommerce│      │ Demo Store│
      └───────────┘      └───────────┘      └───────────┘
```

---

## 2. Universal Commerce Adapter Standard
To ensure universal store compatibility, the AI Associate communicates exclusively with a standardized 4-part interface:
1. **Catalog Search & Filter Interface**:
   * `search_products(query, category_id, min_price, max_price, attributes, limit, offset)`
   * Returns: Normalized list of products with active filter facets.
2. **Product Details Interface**:
   * `get_product_details(product_id)`
   * Returns: Comprehensive product metadata, variant options (sizes, colors), and stock levels.
3. **Cart Mutation Interface**:
   * `add_to_cart(cart_id, variant_id, quantity)`
   * `remove_from_cart(cart_id, item_id)`
   * `get_cart(cart_id)`
   * Returns: Current cart state, subtotal, discount codes, and line items.
4. **Active Shopper Context & Recommendations**:
   * `get_categories()`
   * `get_featured_products()`

---

## 3. Communication Protocol (REST + SSE)
* **Client ➔ Agent**: Shopper messages and active page context sent via `POST /api/v1/chat/message`.
* **Agent ➔ Client**: Responses streamed via **Server-Sent Events (SSE)**.
  * `event: token`: Incremental text chunks for human-like salesperson conversation.
  * `event: ui_action`: Structured commands that the frontend client executes in real-time (e.g. `SET_FILTERS`, `HIGHLIGHT_PRODUCTS`, `SHOW_COMPARISON_MODAL`).
  * `event: cart_update`: Cart state mutations triggered by conversational actions.

---

## 4. Latency & Performance SLAs
* **Time to First Token (TTFT)**: < 800ms.
* **Full Turn Completion**: < 2.5s.
* **Product Search Latency**: < 150ms.
* **Cart Mutation Latency**: < 100ms.
