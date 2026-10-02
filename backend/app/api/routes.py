import logging

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodePilot API"
    }

@router.post("/chat", response_model = ChatResponse)
async def chat(request: ChatRequest):
    try:
        reply = await chat_service.send_message(
            request.message
        )

        return ChatResponse(
            reply = reply,
            model = settings.gemini_model
        )
    except Exception:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code = 502,
            detail="The AI service could not complete the request."
        )