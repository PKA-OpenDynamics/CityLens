# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
FiWARE Smart Data Models
Implementation of standardized data models from https://smartdatamodels.org

Domains:
- Environment: Air quality, weather
- Transportation: Traffic flow, accidents
- Parking: Parking facilities
- Urban Infrastructure: Street lights, water quality
"""

from .environment import (
    AirQualityObserved,
    WeatherObserved,
)
from .transportation import (
    TrafficFlowObserved,
    RoadAccident,
)
from .parking import (
    OffStreetParking,
    ParkingSpot,
)
from .infrastructure import (
    StreetLight,
    WaterQualityObserved,
)
from .citizen import (
    CitizenReport,
)

__all__ = [
    # Environment
    "AirQualityObserved",
    "WeatherObserved",
    # Transportation
    "TrafficFlowObserved",
    "RoadAccident",
    # Parking
    "OffStreetParking",
    "ParkingSpot",
    # Infrastructure
    "StreetLight",
    "WaterQualityObserved",
    # Citizen
    "CitizenReport",
]

