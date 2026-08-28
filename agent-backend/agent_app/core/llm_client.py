"""Google Gemini 2.5 Flash Intelligent LLM Client for ShopAgent v3.0.

Provides structured AI capabilities for hyper-personalization:
- Intent classification with confidence scoring
- Entity extraction from natural language
- Preference signal learning from conversation
- Per-product personalization scoring with reasoning
- Context-aware salesperson response generation
- AI-powered comparison and deep research analysis
"""

from typing import Any, Dict, List, Optional
import os
import json
import logging
import asyncio
from google import genai
from google.genai import types

from agent_app.core.config import settings

logger = logging.getLogger("shopagent.llm")

# LLM call timeout in seconds to ensure zero hung calls
LLM_TIMEOUT_SECONDS = 6.0


# ──────────────────────────────────────────────────────────────────────
# System Prompts
# ──────────────────────────────────────────────────────────────────────

SALES_PERSONA_PROMPT = """You are 'ShopAgent Sales Associate'—a warm, charismatic, charming, enthusiastic, and lovable physical retail sales associate walking right beside the customer in a luxury running & sports footwear boutique.

YOUR PERSONALITY & SALES SECRETS:
1. Warmth & Flattery: Address the shopper respectfully as 'Sir' or 'Boss'. Give sweet, sincere compliments on their style, taste, and physique ("Sir, in this pair you look like an absolute movie superstar hero, haha! 🔥", "You have an eagle's eye for luxury!").
2. Active Persuasion & Deal-Closing: Recommend the best shoe enthusiastically. Highlight how only a couple of pairs are left in their size. Ask cheerfully if you can pack it into their shopping bag right now.
3. Fitting & Cushioning Wisdom: If they have flat feet, wide feet, or knee pain, explain the midsole cushioning (e.g. ReactX foam, Boost, Gore-Tex) like an expert footwear doctor.
4. Formatting: Keep responses concise (2-3 punchy paragraphs max), enthusiastic with emojis, and formatted with markdown bolding. Never break character. Always stay lovable, charismatic, and persuasive!
5. PERSONALIZATION: When shopper preferences are known, reference them naturally. ("Since you love bold colors and train for marathons, THIS is the shoe I was saving just for you!")
6. MULTI-TURN AWARENESS: Reference earlier parts of the conversation naturally when relevant. ("Remember the Pegasus I showed you earlier? Well, this Ultraboost has even MORE cushioning!")
"""

INTENT_CLASSIFICATION_PROMPT = """You are an AI intent classifier for a premium footwear e-commerce store. Classify the customer's message into exactly one intent category.

Intent categories:
- product_search: Looking for shoes, browsing, requesting recommendations
- cart_action: Adding/removing/viewing cart, checkout
- wishlist_action: Save for later, favorites, bookmarks
- compare_products: Comparing two or more shoes, "which is better", "vs"
- deep_research: Complex biomechanical questions, flat feet, marathon training, injury-related
- gift_recommendation: Shopping for someone else, birthday/anniversary gift
- style_advice: Fashion advice, what goes with what, outfit matching
- follow_up: Referring to previous results ("something cheaper", "in black", "the first one")
- reorder: Wants to buy something they bought before
- general_chat: Greeting, thank you, or unrelated conversation

Consider the conversation history for context. A short message like "cheaper?" after a product search is a follow_up, not a product_search."""

ENTITY_EXTRACTION_PROMPT = """You are an AI entity extractor for a premium footwear e-commerce store. Extract structured shopping parameters from the customer's message.

Extract these fields (set to null if not mentioned):
- query: Residual search text after extracting specific fields
- category_id: One of "running-shoes", "trail-outdoor", "lifestyle-sneakers", or null
- min_price: Minimum price in INR (numeric)
- max_price: Maximum price in INR (numeric). Convert "8k" to 8000, "under 10000" to 10000
- brand: Exact brand name (Nike, Adidas, Puma, Salomon) or null
- size: UK shoe size as string or null
- color: Color preference or null
- occasion: Shopping occasion (gift, race day, casual, wedding, etc.) or null
- use_case: Primary use (marathon, daily training, gym, commute, hiking, etc.) or null

Consider the shopper's known profile when the message is ambiguous. If they have a remembered size/budget, don't re-extract unless overridden."""

PREFERENCE_EXTRACTION_PROMPT = """You are an AI preference analyzer for a luxury footwear store. Analyze the customer's message and conversation history to extract preference signals — both positive (likes) and negative (dislikes).

Extract these fields (return empty lists for categories with no signals):
- new_brands_liked: Brand names they show positive interest in
- new_brands_disliked: Brands they explicitly reject or express dislike for
- new_style_signals: Style preferences (minimalist, bold, retro, sporty, etc.)
- new_color_preferences: Color preferences mentioned
- new_foot_conditions: Foot or body conditions (wide feet, high arch, knee pain, plantar fasciitis, etc.)
- new_use_cases: Activities or use cases (marathon, daily run, gym, hiking, office wear, etc.)
- new_occasions: Shopping occasions (birthday gift, race day, date night, etc.)
- budget_update: New budget ceiling in INR if mentioned (null otherwise)
- size_update: New shoe size if mentioned (null otherwise)
- price_sensitivity: One of "budget", "mid-range", "premium", "luxury", or null if unclear
- sentiment: Current shopping mood — "enthusiastic", "cautious", "decisive", "browsing", "frustrated"
- special_notes: Any other notable preferences or requirements as a list of short strings"""

PERSONALIZATION_SCORING_PROMPT = """You are an AI personalization engine for a luxury footwear store. Score how well a product matches this specific shopper's profile and current intent.

For the given product and shopper profile, provide:
- score: A float between 0.0 and 1.0 representing match quality
- reasoning: A one-sentence explanation of WHY this product is good/bad for THIS specific shopper
- match_factors: List of 1-3 positive factors (e.g., "Has ReactX cushioning for your knee pain", "Within your ₹8000 budget")
- concern_factors: List of 0-2 concerns (e.g., "Slightly above your budget", "No wide-fit option available")

Consider: brand affinity, price fit, style DNA match, foot condition suitability, use case alignment, color preferences, and whether we've already recommended this before."""

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]


class ShopAgentLLM:
    """Intelligent Gemini 2.5 Flash Client with Structured AI Capabilities & Resilient Timeouts."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = settings.DEFAULT_MODEL or "gemini-2.5-flash"
        self._client: Optional[genai.Client] = None

        if self.api_key and not self.api_key.startswith("AQ.dummy"):
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client: {e}")

    @property
    def is_available(self) -> bool:
        return bool(self._client and self.api_key)

    async def _generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Optional[Dict[str, Any]]:
        """Generate structured JSON output from Gemini with model cascading and hard timeout."""
        if not self.is_available or not self._client:
            return None

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            response_mime_type="application/json",
        )

        for model_name in [self.model] + [m for m in FALLBACK_MODELS if m != self.model]:
            try:
                response = await asyncio.wait_for(
                    self._client.aio.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=config,
                    ),
                    timeout=LLM_TIMEOUT_SECONDS,
                )
                if response and response.text:
                    text = response.text.strip()
                    if text.startswith("```"):
                        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                    return json.loads(text)
            except asyncio.TimeoutError:
                logger.warning(f"Model {model_name} timed out after {LLM_TIMEOUT_SECONDS}s. Trying next cascade...")
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error from {model_name}: {e}")
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}. Trying next cascade...")

        return None

    async def _generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Generate free-text response from Gemini with model cascading and hard timeout."""
        if not self.is_available or not self._client:
            return None

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        )

        for model_name in [self.model] + [m for m in FALLBACK_MODELS if m != self.model]:
            try:
                response = await asyncio.wait_for(
                    self._client.aio.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=config,
                    ),
                    timeout=LLM_TIMEOUT_SECONDS,
                )
                if response and response.text:
                    return response.text.strip()
            except asyncio.TimeoutError:
                logger.warning(f"Model {model_name} timed out after {LLM_TIMEOUT_SECONDS}s. Trying next cascade...")
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}. Trying next cascade...")

        return None

    # ──────────────────────────────────────────────────────────────────
    # 1. Intent Classification
    # ──────────────────────────────────────────────────────────────────

    async def classify_intent(
        self,
        query: str,
        conversation_history: str = "",
        profile_context: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Classify shopper intent using LLM with structured JSON output."""
        prompt = f"""Shopper Profile: {profile_context or 'New customer'}
Conversation History:
{conversation_history or '(First message)'}

Current Message: "{query}"

Respond with JSON: {{"intent": "<intent_category>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}"""

        return await self._generate_json(INTENT_CLASSIFICATION_PROMPT, prompt, temperature=0.1)

    # ──────────────────────────────────────────────────────────────────
    # 2. Entity Extraction
    # ──────────────────────────────────────────────────────────────────

    async def extract_entities(
        self,
        query: str,
        profile_context: str = "",
        conversation_history: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Extract structured shopping entities from natural language."""
        prompt = f"""Shopper Profile: {profile_context or 'New customer'}
Conversation History:
{conversation_history or '(First message)'}

Current Message: "{query}"

Extract shopping parameters as JSON: {{"query": null, "category_id": null, "min_price": null, "max_price": null, "brand": null, "size": null, "color": null, "occasion": null, "use_case": null}}"""

        return await self._generate_json(ENTITY_EXTRACTION_PROMPT, prompt, temperature=0.1)

    # ──────────────────────────────────────────────────────────────────
    # 3. Preference Signal Extraction
    # ──────────────────────────────────────────────────────────────────

    async def extract_preferences(
        self,
        query: str,
        conversation_history: str = "",
        current_profile_context: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Extract preference signals (likes, dislikes, conditions) from conversation."""
        prompt = f"""Current Shopper Profile: {current_profile_context or 'New customer'}
Conversation History:
{conversation_history or '(First message)'}

Latest Message: "{query}"

Extract preference signals as JSON:
{{
  "new_brands_liked": [],
  "new_brands_disliked": [],
  "new_style_signals": [],
  "new_color_preferences": [],
  "new_foot_conditions": [],
  "new_use_cases": [],
  "new_occasions": [],
  "budget_update": null,
  "size_update": null,
  "price_sensitivity": null,
  "sentiment": null,
  "special_notes": []
}}"""

        return await self._generate_json(PREFERENCE_EXTRACTION_PROMPT, prompt, temperature=0.2)

    # ──────────────────────────────────────────────────────────────────
    # 4. Per-Product Personalization Scoring
    # ──────────────────────────────────────────────────────────────────

    async def score_product_personalization(
        self,
        product: Dict[str, Any],
        profile_context: str,
        query: str,
        conversation_history: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Score how well a product matches this specific shopper."""
        product_info = json.dumps({
            "id": product.get("id"),
            "title": product.get("title"),
            "brand": product.get("brand"),
            "price": product.get("base_price"),
            "description": product.get("description", ""),
            "specs": product.get("specs", {}),
            "variants": [
                {"size": v.get("size"), "stock": v.get("stock", 0)}
                for v in product.get("variants", [])[:5]
            ],
        }, indent=2)

        prompt = f"""Shopper Profile: {profile_context}
Current Query: "{query}"
Conversation Context: {conversation_history or '(First interaction)'}

Product to Score:
{product_info}

Score this product's personalization match as JSON:
{{"score": <0.0-1.0>, "reasoning": "<one sentence>", "match_factors": ["<factor1>", ...], "concern_factors": ["<concern1>", ...]}}"""

        return await self._generate_json(PERSONALIZATION_SCORING_PROMPT, prompt, temperature=0.2)

    async def score_products_batch(
        self,
        products: List[Dict[str, Any]],
        profile_context: str,
        query: str,
        conversation_history: str = "",
        max_products: int = 5,
    ) -> List[Dict[str, Any]]:
        """Score multiple products in a single LLM call for token efficiency."""
        if not self.is_available:
            return []

        products_to_score = products[:max_products]
        products_info = json.dumps([
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "brand": p.get("brand"),
                "price": p.get("base_price"),
                "description": p.get("description", "")[:100],
                "specs": p.get("specs", {}),
            }
            for p in products_to_score
        ], indent=2)

        prompt = f"""Shopper Profile: {profile_context}
Current Query: "{query}"
Conversation Context: {conversation_history or '(First interaction)'}

Score each product's personalization match for this specific shopper.
Products:
{products_info}

Respond as a JSON array with one entry per product:
[{{"product_id": "<id>", "score": <0.0-1.0>, "reasoning": "<one sentence>", "match_factors": ["..."], "concern_factors": ["..."]}}]"""

        result = await self._generate_json(PERSONALIZATION_SCORING_PROMPT, prompt, temperature=0.2)

        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "scores" in result:
            return result["scores"]
        return []

    # ──────────────────────────────────────────────────────────────────
    # 5. Salesperson Response Generation
    # ──────────────────────────────────────────────────────────────────

    async def generate_salesperson_response(
        self,
        user_query: str,
        retrieved_products: List[Dict[str, Any]],
        shopper_profile_context: str = "",
        conversation_history: str = "",
        intent: str = "product_search",
        reflection_notes: List[str] = None,
        personalization_scores: List[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Generate a fully personalized, context-aware salesperson response."""
        catalog_snippet = json.dumps(
            [
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "brand": p.get("brand"),
                    "price": p.get("base_price"),
                    "description": p.get("description", "")[:150],
                }
                for p in retrieved_products[:4]
            ],
            indent=2,
        )

        reflection_context = ""
        if reflection_notes:
            reflection_context = f"\nReflection Notes: {'; '.join(reflection_notes)}"

        personalization_context = ""
        if personalization_scores:
            score_lines = [
                f"- {s.get('reasoning', '')} (Match: {s.get('score', 0):.0%})"
                for s in personalization_scores[:3]
            ]
            personalization_context = f"\nPersonalization Insights:\n" + "\n".join(score_lines)

        prompt = f"""Shopper Profile: {shopper_profile_context or 'New customer'}

Conversation So Far:
{conversation_history or '(First message)'}

Customer's Current Message: "{user_query}"
Detected Intent: {intent}
{reflection_context}
{personalization_context}

Available Products on Showcase:
{catalog_snippet}

Respond as their charming personal sales associate. If products match their needs, pitch the #1 best shoe with personalized reasoning tied to THEIR specific preferences and history. Reference earlier conversation naturally if relevant."""

        return await self._generate_text(SALES_PERSONA_PROMPT, prompt, temperature=0.7)

    # ──────────────────────────────────────────────────────────────────
    # 6. Comparison Analysis
    # ──────────────────────────────────────────────────────────────────

    async def generate_comparison(
        self,
        products: List[Dict[str, Any]],
        profile_context: str = "",
        query: str = "",
        conversation_history: str = "",
    ) -> Optional[str]:
        """Generate AI-powered personalized product comparison."""
        products_detail = json.dumps([
            {
                "title": p.get("title"),
                "brand": p.get("brand"),
                "price": p.get("base_price"),
                "description": p.get("description", ""),
                "specs": p.get("specs", {}),
            }
            for p in products[:3]
        ], indent=2)

        prompt = f"""Shopper Profile: {profile_context or 'New customer'}
Conversation History:
{conversation_history or '(First message)'}

Customer asked: "{query}"
They want to compare these shoes:
{products_detail}

As their charming salesperson, give a side-by-side comparison that references their SPECIFIC preferences, foot conditions, and use cases. End with a personal recommendation for THEM specifically and offer to bag it."""

        return await self._generate_text(SALES_PERSONA_PROMPT, prompt, temperature=0.6)

    # ──────────────────────────────────────────────────────────────────
    # 7. Deep Research Analysis
    # ──────────────────────────────────────────────────────────────────

    async def generate_deep_research(
        self,
        products: List[Dict[str, Any]],
        profile_context: str = "",
        query: str = "",
        conversation_history: str = "",
    ) -> Optional[str]:
        """Generate AI-powered biomechanical research and expert recommendation."""
        products_detail = json.dumps([
            {
                "title": p.get("title"),
                "brand": p.get("brand"),
                "price": p.get("base_price"),
                "description": p.get("description", ""),
                "specs": p.get("specs", {}),
            }
            for p in products[:5]
        ], indent=2)

        research_prompt = f"""Shopper Profile: {profile_context or 'New customer'}
Conversation History:
{conversation_history or '(First message)'}

Customer's Research Question: "{query}"

Available Products in Collection:
{products_detail}

As a footwear biomechanics expert AND charming salesperson:
1. Analyze the customer's specific needs (foot conditions, intended use, biomechanical requirements)
2. Evaluate each product against their needs with match percentages
3. Recommend the #1 best match with expert reasoning
4. Mention a runner-up alternative
5. End with enthusiastic offer to pack their hero match

Use emojis, markdown bolding, and percentages. Keep it engaging and expert-level."""

        return await self._generate_text(SALES_PERSONA_PROMPT, research_prompt, temperature=0.5)

    # ──────────────────────────────────────────────────────────────────
    # Legacy Compatibility
    # ──────────────────────────────────────────────────────────────────

    async def generate_salesperson_pitch(
        self,
        user_query: str,
        retrieved_products: List[Dict[str, Any]],
        shopper_profile: Optional[Any] = None,
        intent: str = "product_search",
    ) -> Optional[str]:
        """Legacy compatibility wrapper — routes to the new context-aware method."""
        profile_context = ""
        if shopper_profile and hasattr(shopper_profile, "get_personalization_context"):
            profile_context = shopper_profile.get_personalization_context()
        elif shopper_profile:
            profile_context = (
                f"Preferred Size: UK {getattr(shopper_profile, 'preferred_size', '10')}, "
                f"Preferred Brands: {getattr(shopper_profile, 'preferred_brands', [])}, "
                f"Notes: {getattr(shopper_profile, 'special_notes', [])}"
            )

        return await self.generate_salesperson_response(
            user_query=user_query,
            retrieved_products=retrieved_products,
            shopper_profile_context=profile_context,
            intent=intent,
        )


llm_client = ShopAgentLLM()
