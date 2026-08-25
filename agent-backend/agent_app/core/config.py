"""AI Associate Brain Configuration Settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Settings for LangGraph AI Store Associate."""
    PROJECT_NAME: str = "ShopAgent AI Associate Brain"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Store Connection & Adapter Configuration
    STORE_ADAPTER_TYPE: str = os.getenv("STORE_ADAPTER_TYPE", "demo")
    STORE_API_URL: str = os.getenv("STORE_API_URL", "http://localhost:8000/api/v1")
    SHOPIFY_STORE_DOMAIN: str = os.getenv("SHOPIFY_STORE_DOMAIN", "")
    SHOPIFY_STOREFRONT_TOKEN: str = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
    
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    TEMPERATURE: float = 0.2
    
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = AgentSettings()
