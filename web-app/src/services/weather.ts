// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Weather Service for fetching weather and AQI data from MongoDB Atlas
 */

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface WeatherData {
  temp?: number;
  feels_like?: number;
  temp_min?: number;
  temp_max?: number;
  pressure?: number;
  humidity?: number;
  visibility?: number;
  wind_speed?: number;
  wind_deg?: number;
  wind_gust?: number;
  clouds?: number;
  rain_1h?: number;
  rain_3h?: number;
  condition?: string;
}

export interface AirQualityData {
  aqi?: number;
  co?: number;
  no?: number;
  no2?: number;
  o3?: number;
  so2?: number;
  pm2_5?: number;
  pm10?: number;
  nh3?: number;
}

export interface RealtimeWeatherResponse {
  location_id: string;
  location_name: string;
  timestamp: string;
  weather?: WeatherData;
  air_quality?: AirQualityData;
  data_age_seconds?: number;
  is_fresh: boolean;
  sources: string[];
}

export interface ForecastPoint {
  timestamp: string;
  temp?: number;
  temp_min?: number;
  temp_max?: number;
  humidity?: number;
  pressure?: number;
  wind_speed?: number;
  wind_deg?: number;
  clouds?: number;
  rain_3h?: number;
  condition?: string;
  visibility?: number;
}

export interface DailyForecast {
  date: string;
  temp_min?: number;
  temp_max?: number;
  condition?: string;
  hourly?: ForecastPoint[]; // Optional - may not exist
  weather_forecasts?: ForecastPoint[]; // Backend format
  air_quality_forecasts?: any[]; // Backend format
}

export interface WeatherForecast {
  id?: string;
  location_id: string;
  location_name: string;
  location: {
    type: string;
    coordinates: number[];
  };
  days: DailyForecast[];
  generated_at: string;
  valid_until: string;
}

class WeatherService {
  /**
   * Get nearby real-time weather data
   */
  async getNearbyRealtime(
    lat: number,
    lon: number,
    radius: number = 10000,
    limit: number = 1
  ): Promise<RealtimeWeatherResponse[]> {
    try {
      const url = `${API_BASE_URL}/weather/realtime/nearby?lat=${lat}&lon=${lon}&radius=${radius}&limit=${limit}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }

      const data: RealtimeWeatherResponse[] = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching nearby realtime weather:', error);
      throw error;
    }
  }

  /**
   * Get real-time weather for a specific location
   */
  async getRealtimeWeather(
    locationId: string,
    useCache: boolean = true
  ): Promise<RealtimeWeatherResponse> {
    try {
      const url = `${API_BASE_URL}/weather/realtime/${locationId}?use_cache=${useCache}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }

      const data: RealtimeWeatherResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching realtime weather:', error);
      throw error;
    }
  }

  /**
   * Get weather forecast for a location
   */
  async getForecast(
    locationId: string,
    days: number = 5
  ): Promise<WeatherForecast> {
    try {
      const url = `${API_BASE_URL}/weather/forecast/${locationId}?days=${days}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Forecast API error: ${response.status}`);
      }

      const data: WeatherForecast = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching forecast:', error);
      throw error;
    }
  }

  /**
   * Get the first 3 forecast points (3-hour forecast)
   */
  getThreeHourForecast(forecast: WeatherForecast): ForecastPoint[] {
    if (!forecast.days || forecast.days.length === 0) {
      return [];
    }

    const points: ForecastPoint[] = [];
    const now = new Date();

    // Get forecast points from today and tomorrow
    for (const day of forecast.days) {
      // Backend returns weather_forecasts, frontend expects hourly
      // Use weather_forecasts if hourly doesn't exist
      const hourlyData = day.hourly || day.weather_forecasts || [];
      
      // Check if hourlyData exists and is an array
      if (!Array.isArray(hourlyData) || hourlyData.length === 0) {
        continue;
      }
      
      for (const hourly of hourlyData) {
        if (!hourly || !hourly.timestamp) {
          continue;
        }
        const pointTime = new Date(hourly.timestamp);
        // Only include future points
        if (pointTime > now && points.length < 3) {
          points.push(hourly);
        }
      }
      if (points.length >= 3) break;
    }

    return points.slice(0, 3);
  }
}

export const weatherService = new WeatherService();
