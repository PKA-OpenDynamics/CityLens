# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
AI Chat API Endpoints
Provides AI-powered chat using Google Gemini with integration to TomTom, OpenWeatherMap, and database
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ai_chat_service import AIChatService
from app.schemas.ai_chat import ChatRequest, ChatResponse, ChatMessage
from app.services.app_auth_service import AppAuthService
from app.db.mongodb_atlas import get_mongodb_atlas
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(
    request: ChatRequest,
    db: Optional[AsyncSession] = Depends(get_db),
    mongodb: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb_atlas),
    authorization: Optional[str] = Header(None)
):
    """
    Chat với AI CityLens
    
    AI có thể trả lời các câu hỏi về:
    - Thời tiết (từ OpenWeatherMap)
    - Chất lượng không khí / AQI (từ OpenWeatherMap)
    - Tình trạng giao thông (từ TomTom)
    - Cơ sở hạ tầng gần bạn (từ database: bệnh viện, trường học, công viên, trạm xe buýt)
    - Tuyến đường gần bạn (từ database)
    
    **Tham số:**
    - **message**: Câu hỏi của bạn
    - **conversation_history**: Lịch sử cuộc trò chuyện (tùy chọn)
    - **user_location**: Vị trí của bạn với latitude và longitude (tùy chọn, nhưng khuyến nghị để có kết quả chính xác hơn)
    - **user_id**: ID người dùng nếu đã đăng nhập (tùy chọn)
    
    **Ví dụ câu hỏi:**
    - "Thời tiết hôm nay như thế nào?"
    - "Chất lượng không khí ở đây ra sao?"
    - "Có bệnh viện nào gần đây không?"
    - "Tình trạng giao thông hiện tại?"
    - "Có trạm xe buýt nào gần tôi không?"
    """
    try:
        # Get user info if authenticated
        user_id = request.user_id
        if authorization and not user_id:
            try:
                token = authorization.replace("Bearer ", "")
                auth_service = AppAuthService(mongodb)
                payload = auth_service.decode_token(token)
                user_id = payload.get("userId")
            except:
                pass  # Continue without user_id
        
        # Initialize AI chat service
        ai_service = AIChatService()
        
        # Convert conversation history format if needed
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Process message
        result = await ai_service.process_message(
            message=request.message,
            conversation_history=conversation_history,
            user_location=request.user_location,
            db=db
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat_with_ai endpoint: {e}")
        logger.error(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý câu hỏi: {str(e)}"
        )


@router.get("/health")
async def ai_chat_health():
    """
    Kiểm tra trạng thái của AI chat service
    """
    from app.core.config import settings
    from app.services.ai_chat_service import AIChatService, GEMINI_AVAILABLE
    
    ai_service = AIChatService()
    
    return {
        "status": "ok" if (settings.GEMINI_API_KEY and ai_service.client and ai_service.model_name) else "not_configured",
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "gemini_available": GEMINI_AVAILABLE,
        "client_initialized": ai_service.client is not None,
        "model_name": ai_service.model_name,
        "api_key_length": len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0,
        "message": f"AI chat service is ready (model: {ai_service.model_name})" if (settings.GEMINI_API_KEY and ai_service.client and ai_service.model_name) else "GEMINI_API_KEY not configured or client not initialized"
    }

