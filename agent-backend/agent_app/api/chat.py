"""Chat & SSE Streaming API Endpoints for AI Store Associate."""

import json
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from agent_app.graph.builder import shopagent_app
from agent_app.schemas.agent_state import AgentResponseDTO, ChatMessageRequest, ShopAgentState

router = APIRouter(prefix="/chat", tags=["AI Store Associate"])


@router.post("/message", response_model=AgentResponseDTO)
async def process_chat_message(request: ChatMessageRequest) -> AgentResponseDTO:
    """Synchronous REST turn processing through LangGraph."""
    initial_state = ShopAgentState(
        session_id=request.session_id,
        shopper_id=request.shopper_id or "shopper_001",
        user_query=request.message,
        messages=[{"role": "user", "content": request.message}],
    )

    try:
        result = await shopagent_app.ainvoke(initial_state)
        return AgentResponseDTO(
            session_id=request.session_id,
            shopper_id=request.shopper_id,
            message=result["final_response"],
            intent=result["intent"],
            emotion=result.get("emotion", "CHARMING_COMPLIMENT"),
            focus_target_id=result.get("focus_target_id"),
            ui_actions=result.get("ui_actions", []),
            products=result.get("retrieved_products", []),
            metadata={"extracted_filters": result.get("extracted_filters", {}).model_dump() if hasattr(result.get("extracted_filters"), "model_dump") else result.get("extracted_filters", {})},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing agent workflow: {str(e)}",
        )


@router.post("/stream")
async def stream_chat_message(request: ChatMessageRequest) -> StreamingResponse:
    """Real-time SSE event stream for interactive sales companion and live UI control."""
    async def event_generator() -> AsyncGenerator[str, None]:
        initial_state = ShopAgentState(
            session_id=request.session_id,
            shopper_id=request.shopper_id or "shopper_001",
            user_query=request.message,
            messages=[{"role": "user", "content": request.message}],
        )

        try:
            result = await shopagent_app.ainvoke(initial_state)

            # 1. Stream Emotion & Target focus first for instant companion avatar reactions
            meta_payload = {
                "emotion": result.get("emotion", "CHARMING_COMPLIMENT"),
                "focus_target_id": result.get("focus_target_id"),
                "intent": result["intent"],
            }
            yield f"event: emotion\ndata: {json.dumps(meta_payload)}\n\n"

            # 2. Stream UI Actions
            for ui_action in result.get("ui_actions", []):
                action_data = ui_action.model_dump() if hasattr(ui_action, "model_dump") else ui_action
                yield f"event: ui_action\ndata: {json.dumps(action_data)}\n\n"

            # 3. Stream tokens of salesperson message
            text = result["final_response"]
            words = text.split(" ")
            for word in words:
                yield f"event: token\ndata: {json.dumps({'token': word + ' '})}\n\n"

            # 4. Stream Done event
            yield f"event: done\ndata: {json.dumps({'intent': result['intent'], 'emotion': result.get('emotion', 'CHARMING_COMPLIMENT'), 'products_count': len(result.get('retrieved_products', []))})}\n\n"

        except Exception as e:
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
