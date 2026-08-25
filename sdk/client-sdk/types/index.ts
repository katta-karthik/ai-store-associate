/**
 * ShopAgent Client Web SDK Type Definitions.
 */

export type EmotionType =
  | 'HYPED'
  | 'CHARMING_COMPLIMENT'
  | 'ANALYTICAL'
  | 'CELEBRATING'
  | 'FIT_ADVISOR';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface UIAction {
  action:
    | 'SET_FILTERS'
    | 'HIGHLIGHT_PRODUCTS'
    | 'OPEN_COMPARISON_MODAL'
    | 'SHOW_RESEARCH_REPORT'
    | 'AVATAR_GLIDE'
    | 'SYNC_CART'
    | 'OPEN_CART_DRAWER'
    | 'SYNC_WISHLIST'
    | 'OPEN_WISHLIST_DRAWER';
  payload?: any;
}

export interface ProductVariant {
  id: string;
  size?: string;
  color?: string;
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
  currency?: string;
  rating?: number;
  review_count?: number;
  primary_image: string;
  images?: string[];
  tags?: string[];
  specs?: Record<string, any>;
  variants?: ProductVariant[];
}

export interface ShopAgentConfig {
  agentApiUrl?: string;
  sessionId?: string;
  shopperId?: string;
  onFilterChange?: (filters: Record<string, any>) => void;
  onHighlightProducts?: (productIds: string[]) => void;
  onAddToCart?: (productId: string, variantId: string) => void;
  onSyncCart?: () => void;
  onSyncWishlist?: () => void;
}
