# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Models
https://smartdatamodels.org

Chuẩn hóa dữ liệu IoT theo các domain:
- Weather: WeatherObserved
- Environment: AirQualityObserved
- Transportation: TrafficFlowObserved, ParkingSpot
- Urban Issues: CivicIssueTracking
"""

from .weather import WeatherObserved, WeatherObservedCreate
from .air_quality import AirQualityObserved, AirQualityObservedCreate
from .traffic import TrafficFlowObserved, TrafficFlowObservedCreate
from .parking import ParkingSpot, ParkingSpotCreate
from .civic_issue import CivicIssueTracking, CivicIssueTrackingCreate

__all__ = [
    "WeatherObserved",
    "WeatherObservedCreate",
    "AirQualityObserved",
    "AirQualityObservedCreate",
    "TrafficFlowObserved",
    "TrafficFlowObservedCreate",
    "ParkingSpot",
    "ParkingSpotCreate",
    "CivicIssueTracking",
    "CivicIssueTrackingCreate",
]
