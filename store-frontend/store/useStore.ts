import { create } from 'zustand';

export interface ProductVariant {
  id: string;
  size: string;
  color: string;
  price: number;
  stock: number;
  sku?: string;
}

export interface Product {
  id: string;
  title: string;
  brand: string;
  category: string;
  description: string;
  base_price: number;
  currency: string;
  rating: number;
  review_count: number;
  primary_image: string;
  tags: string[];
  specs: Record<string, any>;
  variants: ProductVariant[];
}

export interface CartItem {
  item_id: string;
  product_id: string;
  variant_id: string;
  title: string;
  size?: string;
  color?: string;
  unit_price: number;
  quantity: number;
  total_price: number;
  image?: string;
}

export interface WishlistItem {
  item_id: string;
  product_id: string;
  variant_id?: string;
  title: string;
  brand: string;
  price: number;
  size?: string;
  image?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  uiActions?: any[];
  timestamp: string;
}

export interface StoreFilters {
  query: string;
  category: string;
  maxPrice: number;
  brand: string;
  size: string;
}

interface StoreState {
  products: Product[];
  isLoading: boolean;
  filters: StoreFilters;
  highlightedProductIds: string[];
  cart: {
    cart_id: string;
    items: CartItem[];
    item_count: number;
    subtotal: number;
  };
  wishlist: {
    wishlist_id: string;
    items: WishlistItem[];
    item_count: number;
  };
  chatMessages: ChatMessage[];
  isChatOpen: boolean;
  isCartOpen: boolean;
  isWishlistOpen: boolean;
  isStreaming: boolean;

  // Actions
  setFilters: (newFilters: Partial<StoreFilters>) => void;
  setHighlightedProducts: (ids: string[]) => void;
  fetchProducts: () => Promise<void>;
  fetchCart: () => Promise<void>;
  addToCart: (productId: string, variantId: string) => Promise<void>;
  removeFromCart: (itemId: string) => Promise<void>;
  fetchWishlist: () => Promise<void>;
  addToWishlist: (productId: string, variantId?: string) => Promise<void>;
  removeFromWishlist: (itemId: string) => Promise<void>;
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateLastAssistantMessage: (token: string) => void;
  toggleChat: () => void;
  toggleCart: () => void;
  toggleWishlist: () => void;
  setIsStreaming: (status: boolean) => void;
}

const STORE_API_URL = process.env.NEXT_PUBLIC_STORE_API_URL || 'http://localhost:8000/api/v1';

export const useStore = create<StoreState>((set, get) => ({
  products: [],
  isLoading: false,
  filters: {
    query: '',
    category: '',
    maxPrice: 15000,
    brand: '',
    size: '',
  },
  highlightedProductIds: [],
  cart: {
    cart_id: 'cart_shopper_session_001',
    items: [],
    item_count: 0,
    subtotal: 0,
  },
  wishlist: {
    wishlist_id: 'wishlist_shopper_session_001',
    items: [],
    item_count: 0,
  },
  chatMessages: [
    {
      id: 'welcome_msg',
      role: 'assistant',
      content: "👋 Hi! I'm your **ShopAgent AI Associate**. Ask me anything like *'I need road running shoes under ₹8k'* or *'Add Nike Pegasus in size 10 to my cart'*, and I'll take care of it for you!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ],
  isChatOpen: true,
  isCartOpen: false,
  isWishlistOpen: false,
  isStreaming: false,

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));
    get().fetchProducts();
  },

  setHighlightedProducts: (ids) => {
    set({ highlightedProductIds: ids });
  },

  fetchProducts: async () => {
    set({ isLoading: true });
    const { filters } = get();

    const params = new URLSearchParams();
    if (filters.query) params.append('q', filters.query);
    if (filters.category && filters.category !== 'all') params.append('category_id', filters.category);
    if (filters.brand && filters.brand !== 'all') params.append('brand', filters.brand);
    if (filters.size && filters.size !== 'all') params.append('size', filters.size);
    if (filters.maxPrice < 15000) params.append('max_price', filters.maxPrice.toString());
    params.append('in_stock', 'true');

    try {
      const res = await fetch(`${STORE_API_URL}/products?${params.toString()}`);
      if (res.ok) {
        const json = await res.json();
        set({ products: json.data?.items || [] });
      }
    } catch (e) {
      console.error('Error fetching products:', e);
    } finally {
      set({ isLoading: false });
    }
  },

  fetchCart: async () => {
    const { cart } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/cart/${cart.cart_id}`);
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ cart: json.data });
      }
    } catch (e) {
      console.error('Error fetching cart:', e);
    }
  },

  addToCart: async (productId: string, variantId: string) => {
    const { cart } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/cart/${cart.cart_id}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, variant_id: variantId, quantity: 1 }),
      });
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ cart: json.data });
      }
    } catch (e) {
      console.error('Error adding to cart:', e);
    }
  },

  removeFromCart: async (itemId: string) => {
    const { cart } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/cart/${cart.cart_id}/items/${itemId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ cart: json.data });
      }
    } catch (e) {
      console.error('Error removing from cart:', e);
    }
  },

  fetchWishlist: async () => {
    const { wishlist } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/wishlist/${wishlist.wishlist_id}`);
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ wishlist: json.data });
      }
    } catch (e) {
      console.error('Error fetching wishlist:', e);
    }
  },

  addToWishlist: async (productId: string, variantId?: string) => {
    const { wishlist } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/wishlist/${wishlist.wishlist_id}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, variant_id: variantId }),
      });
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ wishlist: json.data });
      }
    } catch (e) {
      console.error('Error adding to wishlist:', e);
    }
  },

  removeFromWishlist: async (itemId: string) => {
    const { wishlist } = get();
    try {
      const res = await fetch(`${STORE_API_URL}/wishlist/${wishlist.wishlist_id}/items/${itemId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        const json = await res.json();
        if (json.data) set({ wishlist: json.data });
      }
    } catch (e) {
      console.error('Error removing from wishlist:', e);
    }
  },

  addChatMessage: (msg) => {
    const newMsg: ChatMessage = {
      ...msg,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    set((state) => ({
      chatMessages: [...state.chatMessages, newMsg],
    }));
  },

  updateLastAssistantMessage: (token: string) => {
    set((state) => {
      const msgs = [...state.chatMessages];
      const lastIndex = msgs.length - 1;
      if (lastIndex >= 0 && msgs[lastIndex].role === 'assistant') {
        msgs[lastIndex] = {
          ...msgs[lastIndex],
          content: msgs[lastIndex].content + token,
        };
      }
      return { chatMessages: msgs };
    });
  },

  toggleChat: () => {
    set((state) => ({ isChatOpen: !state.isChatOpen }));
  },

  toggleCart: () => {
    set((state) => ({ isCartOpen: !state.isCartOpen }));
  },

  toggleWishlist: () => {
    set((state) => ({ isWishlistOpen: !state.isWishlistOpen }));
  },

  setIsStreaming: (status) => {
    set({ isStreaming: status });
  },
}));
