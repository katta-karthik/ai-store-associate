"""Chat & SSE Streaming API Endpoints for AI Store Associate v3.0."""

import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from agent_app.graph.builder import shopagent_app
from agent_app.memory.conversation_store import conversation_store
from agent_app.schemas.agent_state import AgentResponseDTO, ChatMessageRequest, ShopAgentState

logger = logging.getLogger("shopagent.api.chat")
router = APIRouter(prefix="/chat", tags=["AI Store Associate"])


@router.post("/message", response_model=AgentResponseDTO)
async def process_chat_message(request: ChatMessageRequest) -> AgentResponseDTO:
    """Synchronous REST turn processing through LangGraph with persistent conversation history."""
    session_id = request.session_id or "default_session"
    shopper_id = request.shopper_id or "shopper_001"

    # 1. Persist user message in conversation history
    await conversation_store.add_message(
        session_id=session_id,
        shopper_id=shopper_id,
        role="user",
        content=request.message,
    )

    # 2. Fetch history for graph execution
    history = await conversation_store.get_history(session_id, limit=20)

    initial_state = ShopAgentState(
        session_id=session_id,
        shopper_id=shopper_id,
        user_query=request.message,
        messages=[{"role": "user", "content": request.message}],
        conversation_history=history,
    )

    try:
        result = await shopagent_app.ainvoke(initial_state)

        product_ids = [p["id"] for p in result.get("retrieved_products", [])]
        final_message = result.get("final_response", "")

        # 3. Persist assistant response in conversation history
        await conversation_store.add_message(
            session_id=session_id,
            shopper_id=shopper_id,
            role="assistant",
            content=final_message,
            intent=result.get("intent"),
            product_ids=product_ids,
        )

        return AgentResponseDTO(
            session_id=session_id,
            shopper_id=shopper_id,
            message=final_message,
            intent=result.get("intent", "general_chat"),
            emotion=result.get("emotion", "CHARMING_COMPLIMENT"),
            focus_target_id=result.get("focus_target_id"),
            ui_actions=result.get("ui_actions", []),
            products=result.get("retrieved_products", []),
            shopper_profile=result.get("shopper_profile"),
            reflection_notes=result.get("reflection_notes", []),
            personalization_scores=result.get("personalization_scores", []),
            metadata={
                "extracted_filters": result.get("extracted_filters", {}).model_dump()
                if hasattr(result.get("extracted_filters"), "model_dump")
                else result.get("extracted_filters", {}),
                "intent_confidence": result.get("intent_confidence", 1.0),
                "style_context": result.get("style_context"),
            },
        )
    except Exception as e:
        logger.error(f"Error executing agent workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing agent workflow: {str(e)}",
        )


@router.post("/stream")
async def stream_chat_message(request: ChatMessageRequest) -> StreamingResponse:
    """Real-time SSE event stream for interactive sales companion, personalization scores, and live UI control."""
    session_id = request.session_id or "default_session"
    shopper_id = request.shopper_id or "shopper_001"

    # Persist user message
    await conversation_store.add_message(
        session_id=session_id,
        shopper_id=shopper_id,
        role="user",
        content=request.message,
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        history = await conversation_store.get_history(session_id, limit=20)

        initial_state = ShopAgentState(
            session_id=session_id,
            shopper_id=shopper_id,
            user_query=request.message,
            messages=[{"role": "user", "content": request.message}],
            conversation_history=history,
        )

        try:
            result = await shopagent_app.ainvoke(initial_state)

            # 1. Stream Emotion & Target focus for companion avatar reactions
            meta_payload = {
                "emotion": result.get("emotion", "CHARMING_COMPLIMENT"),
                "focus_target_id": result.get("focus_target_id"),
                "intent": result.get("intent", "general_chat"),
            }
            yield f"event: emotion\ndata: {json.dumps(meta_payload)}\n\n"

            # 2. Stream UI Actions
            for ui_action in result.get("ui_actions", []):
                action_data = ui_action.model_dump() if hasattr(ui_action, "model_dump") else ui_action
                yield f"event: ui_action\ndata: {json.dumps(action_data)}\n\n"

            # 3. Stream Personalization Scores
            p_scores = result.get("personalization_scores", [])
            if p_scores:
                scores_data = [s.model_dump() if hasattr(s, "model_dump") else s for s in p_scores]
                yield f"event: personalization\ndata: {json.dumps({'scores': scores_data})}\n\n"

            # 4. Stream tokens of salesperson message
            text = result.get("final_response", "")
            words = text.split(" ")
            for word in words:
                yield f"event: token\ndata: {json.dumps({'token': word + ' '})}\n\n"

            # 5. Persist assistant message in history
            product_ids = [p["id"] for p in result.get("retrieved_products", [])]
            await conversation_store.add_message(
                session_id=session_id,
                shopper_id=shopper_id,
                role="assistant",
                content=text,
                intent=result.get("intent"),
                product_ids=product_ids,
            )

            # 6. Stream Done event with enriched metadata
            done_payload = {
                "intent": result.get("intent"),
                "emotion": result.get("emotion", "CHARMING_COMPLIMENT"),
                "products_count": len(result.get("retrieved_products", [])),
                "shopper_profile": result.get("shopper_profile").model_dump() if result.get("shopper_profile") else None,
            }
            yield f"event: done\ndata: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error in agent workflow: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
