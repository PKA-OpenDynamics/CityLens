# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
AI Chat Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for AI chat"""
    message: str = Field(..., description="User's message/prompt", min_length=1)
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, 
        description="Previous conversation messages for context"
    )
    user_location: Optional[Dict[str, float]] = Field(
        default=None,
        description="User's location with 'latitude' and 'longitude' keys"
    )
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")


class ChatResponse(BaseModel):
    """Response from AI chat"""
    response: str = Field(..., description="AI assistant's response")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Data sources used (e.g., 'OpenWeatherMap', 'TomTom', 'Database')"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the response"
    )

