# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather data helper utilities
"""

from typing import Optional, Dict, Any


def extract_coordinates_from_doc(doc: dict) -> Optional[list]:
    """Extract [lon, lat] coordinates from various document formats"""
    # Try location field first (if exists)
    if "location" in doc:
        loc = doc["location"]
        if isinstance(loc, dict) and "coordinates" in loc:
            coords = loc["coordinates"]
            if isinstance(coords, list) and len(coords) >= 2:
                if all(isinstance(x, (int, float)) for x in coords[:2]):
                    return [float(coords[0]), float(coords[1])]
        elif isinstance(loc, list):
            if len(loc) >= 2 and all(isinstance(x, (int, float)) for x in loc[:2]):
                return [float(loc[0]), float(loc[1])]
            elif len(loc) > 0 and isinstance(loc[0], dict) and "coordinates" in loc[0]:
                nested = loc[0]["coordinates"]
                if isinstance(nested, list) and len(nested) >= 2:
                    return [float(nested[0]), float(nested[1])]
    
    # Try coordinates field - handle GeoJSON object format
    if "coordinates" in doc:
        coords_field = doc["coordinates"]
        # Case 1: coordinates is a GeoJSON object like {"type": "Point", "coordinates": [lon, lat]}
        if isinstance(coords_field, dict) and "coordinates" in coords_field:
            coords = coords_field["coordinates"]
            if isinstance(coords, list) and len(coords) >= 2:
                if all(isinstance(x, (int, float)) for x in coords[:2]):
                    return [float(coords[0]), float(coords[1])]
        # Case 2: coordinates is a direct list [lon, lat]
        elif isinstance(coords_field, list):
            if len(coords_field) >= 2 and all(isinstance(x, (int, float)) for x in coords_field[:2]):
                return [float(coords_field[0]), float(coords_field[1])]
            elif len(coords_field) > 0 and isinstance(coords_field[0], dict):
                if "coordinates" in coords_field[0]:
                    nested = coords_field[0]["coordinates"]
                    if isinstance(nested, list) and len(nested) >= 2:
                        return [float(nested[0]), float(nested[1])]
    
    return None


def normalize_location_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a location document from MongoDB to WeatherLocation format
    
    Handles:
    - Convert _id to id (string)
    - Extract and normalize coordinates
    - Build address if missing
    - Add default external_ids if missing
    - Add default collection_config if missing
    
    Args:
        doc: Raw MongoDB document
        
    Returns:
        Normalized document ready for WeatherLocation model
    """
    # Convert _id to string if present
    doc_id = None
    if "_id" in doc:
        doc_id = str(doc["_id"])
        del doc["_id"]
    
    # Extract coordinates and normalize location field
    coords = extract_coordinates_from_doc(doc)
    if coords:
        doc["location"] = {
            "type": "Point",
            "coordinates": coords
        }
    
    # Set id field
    if doc_id:
        doc["id"] = doc_id
    
    # Build address if missing
    if "address" not in doc:
        address_data = {}
        if "city" in doc:
            address_data["city"] = doc["city"]
        if "district" in doc:
            address_data["district"] = doc["district"]
        if "country" in doc:
            address_data["country_code"] = doc["country"]
            country_map = {"VN": "Vietnam", "US": "United States"}
            address_data["country"] = country_map.get(doc["country"], "Vietnam")
        else:
            address_data["country"] = "Vietnam"
            address_data["country_code"] = "VN"
        
        if address_data:
            doc["address"] = address_data
    
    # External IDs (optional)
    if "external_ids" not in doc:
        doc["external_ids"] = {
            "openweathermap_id": None,
            "openaq_location_id": None
        }
    
    # Collection config (optional)
    if "collection_config" not in doc:
        doc["collection_config"] = {
            "interval_minutes": 60,
            "enabled": True,
            "sources": ["openweathermap"]
        }
    
    return doc


