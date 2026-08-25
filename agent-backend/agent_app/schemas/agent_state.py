"""LangGraph State Schemas for ShopAgent."""

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
    specs_filter: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class UIAction(BaseModel):
    """Real-time UI action for the store frontend to execute."""
    action: str  # e.g. "SET_FILTERS", "HIGHLIGHT_PRODUCTS", "SYNC_CART", "OPEN_CART_DRAWER", "SYNC_WISHLIST"
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
    ui_actions: List[UIAction] = Field(default_factory=list)
    products: List[Dict[str, Any]] = Field(default_factory=list)
    shopper_profile: Optional[ShopperProfile] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ShopAgentState(BaseModel):
    """LangGraph Graph State Model."""
    session_id: str = "default_session"
    shopper_id: str = "shopper_default"
    shopper_profile: Optional[ShopperProfile] = None
    user_query: str = ""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    intent: str = "general_chat"
    extracted_filters: ExtractedFilters = Field(default_factory=ExtractedFilters)
    retrieved_products: List[Dict[str, Any]] = Field(default_factory=list)
    ui_actions: List[UIAction] = Field(default_factory=list)
    final_response: str = ""
    confidence_score: float = 1.0
    error: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
