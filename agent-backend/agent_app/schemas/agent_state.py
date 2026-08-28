"""LangGraph State Schemas for ShopAgent v3.0 — AI Hyper-Personalization Engine."""

from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from agent_app.memory.shopper_memory import ShopperProfile


class ExtractedFilters(BaseModel):
    """Filters extracted from natural language shopper query."""
    query: Optional[str] = None
    category_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    occasion: Optional[str] = None
    use_case: Optional[str] = None
    specs_filter: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ProductPersonalizationScore(BaseModel):
    """Per-product AI personalization score with reasoning."""
    product_id: str
    score: float = 0.0  # 0.0–1.0
    reasoning: str = ""
    match_factors: List[str] = Field(default_factory=list)
    concern_factors: List[str] = Field(default_factory=list)


class UIAction(BaseModel):
    """Real-time UI action for the store frontend to execute."""
    action: str  # e.g. "SET_FILTERS", "HIGHLIGHT_PRODUCTS", "SYNC_CART", "OPEN_CART_DRAWER", "SYNC_WISHLIST", "AVATAR_GLIDE", "SET_EMOTION"
    payload: Dict[str, Any] = Field(default_factory=dict)


class ChatMessageRequest(BaseModel):
    """Incoming shopper message request."""
    session_id: str = "default_session"
    shopper_id: Optional[str] = None
    message: str
    active_filters: Optional[Dict[str, Any]] = None
    current_product_id: Optional[str] = None


class AgentResponseDTO(BaseModel):
    """Complete structured response from the AI Associate."""
    session_id: str
    shopper_id: Optional[str] = None
    message: str
    intent: str
    emotion: str = "HYPED"  # HYPED, CHARMING_COMPLIMENT, ANALYTICAL, CELEBRATING, FIT_ADVISOR, SASSY_DEAL
    focus_target_id: Optional[str] = None
    ui_actions: List[UIAction] = Field(default_factory=list)
    products: List[Dict[str, Any]] = Field(default_factory=list)
    shopper_profile: Optional[ShopperProfile] = None
    reflection_notes: List[str] = Field(default_factory=list)
    personalization_scores: List[ProductPersonalizationScore] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ShopAgentState(BaseModel):
    """LangGraph Graph State Model with AI Hyper-Personalization."""
    session_id: str = "default_session"
    shopper_id: str = "shopper_default"
    shopper_profile: Optional[ShopperProfile] = None
    user_query: str = ""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    intent: str = "general_chat"
    intent_confidence: float = 1.0
    emotion: str = "HYPED"
    focus_target_id: Optional[str] = None
    extracted_filters: ExtractedFilters = Field(default_factory=ExtractedFilters)
    retrieved_products: List[Dict[str, Any]] = Field(default_factory=list)
    personalization_scores: List[ProductPersonalizationScore] = Field(default_factory=list)
    style_context: Optional[str] = None
    follow_up_context: Optional[str] = None
    ui_actions: List[UIAction] = Field(default_factory=list)
    reflection_notes: List[str] = Field(default_factory=list)
    final_response: str = ""
    confidence_score: float = 1.0
    error: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
