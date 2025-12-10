# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
AI Chat Service using Google Gemini
Integrates with TomTom, OpenWeatherMap, and database for real-time data
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from google import genai
    GEMINI_AVAILABLE = True
except (ImportError, TypeError, Exception) as e:
    logger.warning(f"Failed to import google.genai: {e}")
    GEMINI_AVAILABLE = False
    genai = None

from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText
from app.models.facility import PublicFacility, TransportFacility
from app.models.geographic import Street, POI


class AIChatService:
    """Service for AI-powered chat with Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        self.model_name = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured")
        elif not GEMINI_AVAILABLE:
            logger.warning("google.genai package not installed or import failed")
        else:
            try:
                # Initialize client with API key
                self.client = genai.Client(api_key=self.api_key)
                
                # Use Gemini 2.5 Flash as default (most efficient)
                # Will fallback to other models if this fails during actual API call
                self.model_name = 'gemini-2.5-flash'
                logger.info(f"Gemini client initialized with model: {self.model_name}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                self.client = None
                self.model_name = None
    
    async def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_location: Optional[Dict[str, float]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate AI response
        
        Args:
            message: User's message
            conversation_history: Previous messages
            user_location: User's location (lat, lon)
            db: Database session for querying facilities/routes
        
        Returns:
            Dict with response, sources, and metadata
        """
        if not self.client or not self.model_name:
            error_msg = "Xin lỗi, tính năng AI chat chưa được cấu hình."
            if not GEMINI_AVAILABLE:
                error_msg += " Lỗi: google.genai không thể import (có thể do Python version không tương thích). Vui lòng sử dụng Python 3.11 hoặc chạy với Docker (tự động dùng Python 3.11)."
            elif not self.api_key:
                error_msg += " GEMINI_API_KEY chưa được cấu hình trong .env file."
            else:
                error_msg += " Vui lòng liên hệ quản trị viên."
            
            return {
                "response": error_msg,
                "sources": [],
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "error": "Client not initialized",
                    "gemini_available": GEMINI_AVAILABLE,
                    "api_key_configured": bool(self.api_key),
                    "client_initialized": self.client is not None,
                    "model_name": self.model_name
                }
            }
        
        # Analyze intent and gather data
        intent = self._analyze_intent(message)
        sources = []
        context_data = {}
        
        # Gather relevant data based on intent
        if user_location:
            lat = user_location.get("latitude")
            lon = user_location.get("longitude")
            
            if intent.get("weather") or intent.get("aqi"):
                weather_data = await self._get_weather_data(lat, lon)
                if weather_data:
                    context_data["weather"] = weather_data
                    sources.append("OpenWeatherMap")
            
            if intent.get("aqi") or intent.get("air_quality"):
                aqi_data = await self._get_aqi_data(lat, lon)
                if aqi_data:
                    context_data["air_quality"] = aqi_data
                    sources.append("OpenWeatherMap")
            
            if intent.get("traffic") or intent.get("congestion"):
                traffic_data = await self._get_traffic_data(lat, lon)
                if traffic_data:
                    context_data["traffic"] = traffic_data
                    sources.append("TomTom")
            
            if intent.get("facilities") or intent.get("services"):
                if db is not None:
                    facilities_data = await self._get_facilities_nearby(
                        db, lat, lon, intent.get("facility_type")
                    )
                    if facilities_data:
                        context_data["facilities"] = facilities_data
                        sources.append("Database")
            
            if intent.get("routes") or intent.get("streets"):
                if db is not None:
                    routes_data = await self._get_routes_nearby(db, lat, lon)
                    if routes_data:
                        context_data["routes"] = routes_data
                        sources.append("Database")
        
        # Build prompt for Gemini
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(message, context_data, conversation_history, user_location)
        
        try:
            # Generate response using new API
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            logger.info(f"Generating AI response for message: {message[:50]}...")
            
            # Try models in order of preference
            model_names = [
                'gemini-2.5-flash',      # Gemini 2.5 Flash (recommended)
                'gemini-2.5-pro',        # Gemini 2.5 Pro
                'gemini-1.5-flash',      # Fallback to 1.5
                'gemini-1.5-pro',
            ]
            
            # Start with configured model, then try others if it fails
            models_to_try = [self.model_name] + [m for m in model_names if m != self.model_name]
            response = None
            used_model = None
            model_errors: List[str] = []
            
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    used_model = model_name
                    # Update model_name for future calls if this one works
                    if model_name != self.model_name:
                        self.model_name = model_name
                        logger.info(f"Switched to model: {model_name}")
                    break
                except Exception as model_error:
                    logger.warning(f"Model {model_name} failed: {model_error}")
                    model_errors.append(f"{model_name}: {model_error}")
                    continue
            
            if not response:
                raise Exception(f"All models failed. Tried: {models_to_try}. Errors: {model_errors}")
            
            return {
                "response": self._sanitize_response(response.text),
                "sources": sources,
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "intent": intent,
                    "has_location": user_location is not None,
                    "model": used_model,
                    "model_errors": model_errors
                }
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error generating AI response: {e}")
            logger.error(f"Traceback: {error_trace}")
            return {
                "response": self._sanitize_response(f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn: {str(e)}. Vui lòng thử lại sau."),
                "sources": sources,
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "model_errors": model_errors if 'model_errors' in locals() else None
                }
            }
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent from message"""
        message_lower = message.lower()
        
        intent = {
            "weather": any(word in message_lower for word in ["thời tiết", "nhiệt độ", "mưa", "nắng", "gió", "weather", "temperature"]),
            "aqi": any(word in message_lower for word in ["chất lượng không khí", "aqi", "pm2.5", "pm10", "ô nhiễm", "air quality"]),
            "traffic": any(word in message_lower for word in ["tắc đường", "giao thông", "lưu lượng", "traffic", "congestion", "kẹt xe"]),
            "facilities": any(word in message_lower for word in ["bệnh viện", "trường học", "công viên", "cơ sở", "dịch vụ", "hospital", "school", "facility"]),
            "routes": any(word in message_lower for word in ["đường", "tuyến", "route", "street", "đi đường nào"]),
            "facility_type": None
        }
        
        # Detect specific facility types
        if "bệnh viện" in message_lower or "hospital" in message_lower:
            intent["facility_type"] = "hospital"
        elif "trường" in message_lower or "school" in message_lower:
            intent["facility_type"] = "school"
        elif "công viên" in message_lower or "park" in message_lower:
            intent["facility_type"] = "park"
        elif "trạm xe buýt" in message_lower or "bus" in message_lower:
            intent["facility_type"] = "bus_stop"
        
        return intent
    
    async def _get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get weather data from OpenWeatherMap"""
        try:
            from app.adapters.openweathermap import OpenWeatherMapAdapter
            adapter = OpenWeatherMapAdapter()
            entity, _ = await adapter.fetch_weather(lat, lon, "Location")
            
            return {
                "temperature": entity.get("temperature", {}).get("value"),
                "feels_like": entity.get("feelsLikeTemperature", {}).get("value"),
                "humidity": entity.get("humidity", {}).get("value"),
                "description": entity.get("description", {}).get("value"),
                "wind_speed": entity.get("windSpeed", {}).get("value"),
                "pressure": entity.get("pressure", {}).get("value")
            }
        except Exception as e:
            logger.warning(f"Error fetching weather: {e}")
            return None
    
    async def _get_aqi_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get air quality data from OpenWeatherMap"""
        try:
            from app.adapters.openweathermap import OpenWeatherMapAdapter
            adapter = OpenWeatherMapAdapter()
            entity = await adapter.fetch_air_quality(lat, lon, "Location")
            
            if entity:
                return {
                    "aqi": entity.get("aqi", {}).get("value"),
                    "pm25": entity.get("pm25", {}).get("value"),
                    "pm10": entity.get("pm10", {}).get("value"),
                    "no2": entity.get("no2", {}).get("value"),
                    "o3": entity.get("o3", {}).get("value")
                }
        except Exception as e:
            logger.warning(f"Error fetching AQI: {e}")
            return None
    
    async def _get_traffic_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get traffic data from TomTom"""
        try:
            from app.adapters.tomtom import TomTomAdapter
            adapter = TomTomAdapter()
            entity = await adapter.fetch_traffic_flow(lat, lon, location_name="Location")
            
            return {
                "current_speed": entity.get("averageVehicleSpeed", {}).get("value"),
                "free_flow_speed": entity.get("averageVehicleSpeedFreeFlow", {}).get("value"),
                "congestion_level": entity.get("congestionLevel", {}).get("value"),
                "travel_time": entity.get("travelTime", {}).get("value")
            }
        except Exception as e:
            logger.warning(f"Error fetching traffic: {e}")
            return None
    
    async def _get_facilities_nearby(
        self,
        db: AsyncSession,
        lat: float,
        lon: float,
        facility_type: Optional[str] = None,
        radius_meters: float = 2000,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get nearby facilities from database"""
        try:
            point_wkt = f"POINT({lon} {lat})"
            facilities = []
            
            # Query public facilities
            query = select(PublicFacility).where(
                ST_DWithin(
                    PublicFacility.location,
                    ST_GeomFromText(point_wkt, 4326),
                    radius_meters / 111319.0
                )
            )
            
            if facility_type:
                query = query.where(PublicFacility.category == facility_type)
            
            query = query.limit(limit)
            result = await db.execute(query)
            public_facilities = result.scalars().all()
            
            for facility in public_facilities:
                # Extract coordinates from geometry
                coord_result = await db.execute(
                    text("SELECT ST_X(location) as lon, ST_Y(location) as lat FROM public_facilities WHERE id = :id"),
                    {"id": facility.id}
                )
                coord = coord_result.fetchone()
                
                facilities.append({
                    "name": facility.name,
                    "category": facility.category,
                    "address": facility.address,
                    "phone": facility.phone,
                    "latitude": coord.lat if coord else None,
                    "longitude": coord.lon if coord else None
                })
            
            # Query transport facilities
            query_transport = select(TransportFacility).where(
                ST_DWithin(
                    TransportFacility.location,
                    ST_GeomFromText(point_wkt, 4326),
                    radius_meters / 111319.0
                )
            )
            
            if facility_type == "bus_stop":
                query_transport = query_transport.where(TransportFacility.facility_type == "bus_stop")
            
            query_transport = query_transport.limit(limit)
            result_transport = await db.execute(query_transport)
            transport_facilities = result_transport.scalars().all()
            
            for facility in transport_facilities:
                coord_result = await db.execute(
                    text("SELECT ST_X(location) as lon, ST_Y(location) as lat FROM transport_facilities WHERE id = :id"),
                    {"id": facility.id}
                )
                coord = coord_result.fetchone()
                
                facilities.append({
                    "name": facility.name,
                    "category": facility.facility_type,
                    "line_number": facility.line_number,
                    "latitude": coord.lat if coord else None,
                    "longitude": coord.lon if coord else None
                })
            
            return facilities if facilities else None
        except Exception as e:
            logger.warning(f"Error fetching facilities: {e}")
            return None
    
    async def _get_routes_nearby(
        self,
        db: AsyncSession,
        lat: float,
        lon: float,
        radius_meters: float = 1000,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get nearby streets/routes from database"""
        try:
            point_wkt = f"POINT({lon} {lat})"
            
            query = select(Street).where(
                ST_DWithin(
                    Street.geometry,
                    ST_GeomFromText(point_wkt, 4326),
                    radius_meters / 111319.0
                )
            ).where(Street.name.isnot(None)).limit(limit)
            
            result = await db.execute(query)
            streets = result.scalars().all()
            
            routes = []
            for street in streets:
                routes.append({
                    "name": street.name,
                    "highway_type": street.highway_type,
                    "length": getattr(street, 'length', None)
                })
            
            return routes if routes else None
        except Exception as e:
            logger.warning(f"Error fetching routes: {e}")
            return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Gemini"""
        return """Bạn là trợ lý AI thông minh của CityLens, một nền tảng thành phố thông minh tại Việt Nam.

Nhiệm vụ của bạn:
1. Trả lời các câu hỏi về thời tiết, chất lượng không khí, giao thông, cơ sở hạ tầng và dịch vụ công cộng
2. Sử dụng dữ liệu thời gian thực được cung cấp để đưa ra câu trả lời chính xác
3. Trả lời bằng tiếng Việt một cách tự nhiên, thân thiện và dễ hiểu
4. Nếu không có dữ liệu, hãy thông báo rõ ràng và đề xuất cách khác để người dùng có thể tìm thông tin
5. **QUAN TRỌNG**: Bạn có thể biết vị trí hiện tại của người dùng thông qua tọa độ GPS (latitude, longitude) được cung cấp. Khi người dùng hỏi về vị trí của họ, hãy sử dụng thông tin tọa độ này để trả lời. Bạn có thể mô tả vị trí dựa trên tọa độ và các cơ sở hạ tầng gần đó.

Hãy luôn cung cấp thông tin hữu ích và thực tế dựa trên dữ liệu được cung cấp."""
    
    def _build_user_prompt(
        self,
        message: str,
        context_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_location: Optional[Dict[str, float]] = None
    ) -> str:
        """Build user prompt with context data"""
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Lịch sử cuộc trò chuyện:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{'Người dùng' if role == 'user' else 'Trợ lý'}: {content}")
            prompt_parts.append("")
        
        # Add user location information
        if user_location:
            lat = user_location.get("latitude")
            lon = user_location.get("longitude")
            prompt_parts.append(f"**Vị trí hiện tại của người dùng:**")
            prompt_parts.append(f"- Tọa độ GPS: {lat}, {lon}")
            prompt_parts.append(f"- Bạn có thể sử dụng thông tin này để trả lời các câu hỏi về vị trí của người dùng.")
            prompt_parts.append("")
        
        # Add context data
        if context_data:
            prompt_parts.append("Dữ liệu thời gian thực hiện có:")
            
            if "weather" in context_data:
                weather = context_data["weather"]
                prompt_parts.append(f"- Thời tiết: Nhiệt độ {weather.get('temperature')}°C, cảm giác như {weather.get('feels_like')}°C")
                prompt_parts.append(f"  Độ ẩm: {weather.get('humidity')}%, Mô tả: {weather.get('description')}")
                prompt_parts.append(f"  Tốc độ gió: {weather.get('wind_speed')} m/s, Áp suất: {weather.get('pressure')} hPa")
            
            if "air_quality" in context_data:
                aqi = context_data["air_quality"]
                prompt_parts.append(f"- Chất lượng không khí: AQI {aqi.get('aqi')}")
                prompt_parts.append(f"  PM2.5: {aqi.get('pm25')} µg/m³, PM10: {aqi.get('pm10')} µg/m³")
                prompt_parts.append(f"  NO2: {aqi.get('no2')} µg/m³, O3: {aqi.get('o3')} µg/m³")
            
            if "traffic" in context_data:
                traffic = context_data["traffic"]
                prompt_parts.append(f"- Giao thông: Tốc độ hiện tại {traffic.get('current_speed')} km/h")
                prompt_parts.append(f"  Tốc độ tự do: {traffic.get('free_flow_speed')} km/h")
                prompt_parts.append(f"  Mức độ tắc nghẽn: {traffic.get('congestion_level')}%")
                prompt_parts.append(f"  Thời gian di chuyển: {traffic.get('travel_time')} giây")
            
            if "facilities" in context_data:
                facilities = context_data["facilities"]
                prompt_parts.append(f"- Cơ sở hạ tầng gần đây ({len(facilities)} địa điểm):")
                for fac in facilities[:5]:  # Top 5
                    prompt_parts.append(f"  + {fac.get('name')} ({fac.get('category')})")
                    if fac.get('address'):
                        prompt_parts.append(f"    Địa chỉ: {fac.get('address')}")
            
            if "routes" in context_data:
                routes = context_data["routes"]
                prompt_parts.append(f"- Tuyến đường gần đây ({len(routes)} tuyến):")
                for route in routes[:5]:  # Top 5
                    prompt_parts.append(f"  + {route.get('name')} ({route.get('highway_type')})")
            
            prompt_parts.append("")
        
        # Add user message
        prompt_parts.append(f"Câu hỏi của người dùng: {message}")
        prompt_parts.append("")
        prompt_parts.append("Hãy trả lời câu hỏi dựa trên dữ liệu trên một cách tự nhiên và hữu ích:")
        
        return "\n".join(prompt_parts)
    
    def _sanitize_response(self, text: str) -> str:
        """Remove markdown bold/italics and trim whitespace"""
        if not text:
            return text
        sanitized = text.replace("**", "").replace("__", "")
        sanitized = sanitized.strip()
        return sanitized

