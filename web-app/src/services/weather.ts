// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Weather Service for fetching weather and AQI data from MongoDB Atlas
 */

import { API_BASE_URL, WEATHER_API_BASE_URL } from '../config/env';

// Sử dụng API_BASE_URL từ env.ts
const WEATHER_API_BASE = API_BASE_URL;
console.log('[WeatherService] WEATHER_API_BASE:', WEATHER_API_BASE);
const OPENWEATHER_API_KEY = process.env.EXPO_PUBLIC_OPENWEATHER_API_KEY;

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
  private parseLatLon(locationId: string): { lat: number; lon: number } | null {
    if (!locationId) return null;
    const parts = locationId.split(',').map((p) => Number(p.trim()));
    if (parts.length === 2 && !Number.isNaN(parts[0]) && !Number.isNaN(parts[1])) {
      return { lat: parts[0], lon: parts[1] };
    }
    return null;
  }

  /**
   * Directly fetch AQI from OpenWeather (air pollution API).
   */
  private async getAirQualityDirectFromOpenWeather(
    lat: number,
    lon: number
  ): Promise<AirQualityData | undefined> {
    if (!OPENWEATHER_API_KEY) return undefined;

    const url = `https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${OPENWEATHER_API_KEY}`;
    const response = await fetch(url);
    if (!response.ok) {
      console.warn('OpenWeather AQI non-200', { url, status: response.status });
      return undefined;
    }

    const data = await response.json();
    const entry = data?.list?.[0];
    if (!entry) return undefined;

    const components = entry.components || {};
    return {
      aqi: entry.main?.aqi, // 1-5 scale
      co: components.co,
      no: components.no,
      no2: components.no2,
      o3: components.o3,
      so2: components.so2,
      pm2_5: components.pm2_5,
      pm10: components.pm10,
      nh3: components.nh3,
    };
  }

  /**
   * Directly fetch forecast from OpenWeather (client-side).
   * Requires EXPO_PUBLIC_OPENWEATHER_API_KEY.
   */
  private async getForecastDirectFromOpenWeather(
    lat: number,
    lon: number,
    days: number = 5
  ): Promise<WeatherForecast> {
    if (!OPENWEATHER_API_KEY) {
      throw new Error('Missing EXPO_PUBLIC_OPENWEATHER_API_KEY for direct forecast.');
    }

    // Use 5-day/3-hour forecast API
    const url = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${OPENWEATHER_API_KEY}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`OpenWeather forecast error: ${response.status}`);
    }

    const data = await response.json();
    const list = data?.list || [];
    const city = data?.city || {};

    // Map each 3-hour item to ForecastPoint
    const forecastPoints: ForecastPoint[] = list.map((item: any) => ({
      timestamp: item?.dt_txt || (item?.dt ? new Date(item.dt * 1000).toISOString() : ''),
      temp: item?.main?.temp,
      temp_min: item?.main?.temp_min,
      temp_max: item?.main?.temp_max,
      humidity: item?.main?.humidity,
      pressure: item?.main?.pressure,
      wind_speed: item?.wind?.speed,
      wind_deg: item?.wind?.deg,
      clouds: item?.clouds?.all,
      rain_3h: item?.rain?.['3h'],
      condition: item?.weather?.[0]?.description,
      visibility: item?.visibility,
    }));

    // Group by date for daily min/max
    const daysMap: Record<
      string,
      { temps: number[]; min: number; max: number; condition?: string; points: ForecastPoint[] }
    > = {};

    for (const point of forecastPoints) {
      const dateKey = point.timestamp ? point.timestamp.split('T')[0] : '';
      if (!dateKey) continue;
      if (!daysMap[dateKey]) {
        daysMap[dateKey] = { temps: [], min: Number.POSITIVE_INFINITY, max: Number.NEGATIVE_INFINITY, points: [] };
      }
      const bucket = daysMap[dateKey];
      if (typeof point.temp === 'number') {
        bucket.temps.push(point.temp);
        bucket.min = Math.min(bucket.min, point.temp_min ?? point.temp);
        bucket.max = Math.max(bucket.max, point.temp_max ?? point.temp);
      }
      if (!bucket.condition && point.condition) {
        bucket.condition = point.condition;
      }
      bucket.points.push(point);
    }

    const daily: DailyForecast[] = Object.entries(daysMap)
      .slice(0, days)
      .map(([date, bucket]) => ({
        date,
        temp_min: bucket.min === Number.POSITIVE_INFINITY ? undefined : bucket.min,
        temp_max: bucket.max === Number.NEGATIVE_INFINITY ? undefined : bucket.max,
        condition: bucket.condition,
        hourly: bucket.points,
        weather_forecasts: bucket.points,
        air_quality_forecasts: [],
      }));

    const firstPoint = forecastPoints[0];
    const generatedAt = new Date().toISOString();

    return {
      id: undefined,
      location_id: `${lat},${lon}`,
      location_name: city?.name || 'Unknown',
      location: {
        type: 'Point',
        coordinates: [lon, lat],
      },
      days: daily,
      generated_at: generatedAt,
      valid_until: daily?.[daily.length - 1]?.date || generatedAt,
    };
  }

  /**
   * Get nearby real-time weather data
   */
  async getNearbyRealtime(
    lat: number,
    lon: number,
    radius: number = 10000, // kept for compatibility with callers; not used by API
    limit: number = 1 // kept for compatibility with callers; not used by API
  ): Promise<RealtimeWeatherResponse[]> {
    try {
      // Use the documented realtime endpoint:
      // GET /api/v1/realtime/weather/latest?latitude=<lat>&longitude=<lon>
      const base = WEATHER_API_BASE.replace(/\/$/, '');
      const url = `${base}/realtime/weather/latest?latitude=${lat}&longitude=${lon}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.warn('Weather API non-200', { url, status: response.status });
        throw new Error(`Weather API error: ${response.status}`);
      }

      const raw = await response.json();

      // Map backend response to existing frontend shape
      const mapped: RealtimeWeatherResponse = {
        location_id: `${raw?.location?.latitude ?? lat},${raw?.location?.longitude ?? lon}`,
        location_name: raw?.location?.city || raw?.location?.name || 'Unknown',
        timestamp: raw?.timestamp || new Date().toISOString(),
        weather: {
          temp: raw?.weather?.temperature,
          feels_like: raw?.weather?.feels_like,
          humidity: raw?.weather?.humidity,
          pressure: raw?.weather?.pressure,
          wind_speed: raw?.weather?.wind_speed,
          clouds: raw?.weather?.clouds,
          visibility: raw?.weather?.visibility,
          condition: raw?.weather?.description,
        },
        // Air quality not provided by this endpoint
        air_quality: undefined,
        data_age_seconds: undefined,
        is_fresh: true,
        sources: raw?.source ? [raw.source] : [],
      };

      // Fetch AQI directly if key available (non-blocking)
      if (OPENWEATHER_API_KEY) {
        try {
          const aqi = await this.getAirQualityDirectFromOpenWeather(lat, lon);
          if (aqi) {
            mapped.air_quality = aqi;
            mapped.sources = [...mapped.sources, 'OpenWeatherMap AQI'];
          }
        } catch (err) {
          console.warn('OpenWeather AQI fetch failed', err);
        }
      }

      return [mapped];
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
      const coords = this.parseLatLon(locationId);

      // Prefer /realtime/weather/latest if we have coordinates (avoid 404 on old endpoints)
      if (coords) {
        const base = WEATHER_API_BASE.replace(/\/$/, '');
        const latestUrl = `${base}/realtime/weather/latest?latitude=${coords.lat}&longitude=${coords.lon}`;
        const res = await fetch(latestUrl, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        if (res.ok) {
          const raw = await res.json();
          const mapped: RealtimeWeatherResponse = {
            location_id: `${raw?.location?.latitude ?? coords.lat},${raw?.location?.longitude ?? coords.lon}`,
            location_name: raw?.location?.city || raw?.location?.name || 'Unknown',
            timestamp: raw?.timestamp || new Date().toISOString(),
            weather: {
              temp: raw?.weather?.temperature,
              feels_like: raw?.weather?.feels_like,
              humidity: raw?.weather?.humidity,
              pressure: raw?.weather?.pressure,
              wind_speed: raw?.weather?.wind_speed,
              clouds: raw?.weather?.clouds,
              visibility: raw?.weather?.visibility,
              condition: raw?.weather?.description,
            },
            air_quality: undefined,
            data_age_seconds: undefined,
            is_fresh: true,
            sources: raw?.source ? [raw.source] : [],
          };
          if (OPENWEATHER_API_KEY) {
            try {
              const aqi = await this.getAirQualityDirectFromOpenWeather(
                raw?.location?.latitude ?? coords.lat,
                raw?.location?.longitude ?? coords.lon
              );
              if (aqi) {
                mapped.air_quality = aqi;
                mapped.sources = [...mapped.sources, 'OpenWeatherMap AQI'];
              }
            } catch (err) {
              console.warn('OpenWeather AQI fetch failed (latest fallback)', err);
            }
          }
          return mapped;
        } else {
          console.warn('Weather latest endpoint non-200', res.status);
        }
      }

      // Legacy endpoints (may 404 on some deployments)
      const urls = [
        `${WEATHER_API_BASE}/weather/realtime/${locationId}?use_cache=${useCache}`,
        `${WEATHER_API_BASE}/app/weather/realtime/${locationId}?use_cache=${useCache}`,
      ];

      for (const url of urls) {
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data: RealtimeWeatherResponse = await response.json();
          const coordsFromId = this.parseLatLon(data.location_id || locationId);
          if (coordsFromId && OPENWEATHER_API_KEY) {
            try {
              const aqi = await this.getAirQualityDirectFromOpenWeather(coordsFromId.lat, coordsFromId.lon);
              if (aqi) {
                data.air_quality = aqi;
                data.sources = data.sources ? [...data.sources, 'OpenWeatherMap AQI'] : ['OpenWeatherMap AQI'];
              }
            } catch (err) {
              console.warn('OpenWeather AQI fetch failed (legacy)', err);
            }
          }
          return data;
        }

        // If endpoint not found (404), continue to next URL instead of throwing
        if (response.status === 404) {
          continue;
        }
      }

      throw new Error('Weather API error');
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
      // If we can parse lat/lon and have OpenWeather key, prefer direct forecast
      const coords = this.parseLatLon(locationId);
      if (coords && OPENWEATHER_API_KEY) {
        return await this.getForecastDirectFromOpenWeather(coords.lat, coords.lon, days);
      }

      // Backend currently has no forecast endpoint in Realtime; gracefully fall back
      // to latest weather and synthesize a minimal forecast-like object.
      const base = WEATHER_API_BASE.replace(/\/$/, '');
      const url = coords
        ? `${base}/realtime/weather/latest?latitude=${coords.lat}&longitude=${coords.lon}`
        : `${base}/realtime/weather/latest`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.warn('Forecast fallback non-200', { url, status: response.status });
        throw new Error(`Forecast API error: ${response.status}`);
      }

      const raw = await response.json();
      const nowIso = raw?.timestamp || new Date().toISOString();

      const day: DailyForecast = {
        date: nowIso.split('T')[0],
        temp_min: raw?.weather?.temp_min ?? raw?.weather?.temperature,
        temp_max: raw?.weather?.temp_max ?? raw?.weather?.temperature,
        condition: raw?.weather?.description,
        hourly: [], // no hourly data available from this endpoint
        weather_forecasts: [],
        air_quality_forecasts: [],
      };

      return {
        id: undefined,
        location_id: locationId,
        location_name: raw?.location?.city || raw?.location?.name || 'Unknown',
        location: {
          type: 'Point',
          coordinates: [
            raw?.location?.longitude ?? coords?.lon ?? 0,
            raw?.location?.latitude ?? coords?.lat ?? 0,
          ],
        },
        days: [day],
        generated_at: nowIso,
        valid_until: nowIso,
      };
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

    const candidates: ForecastPoint[] = [];
    const now = new Date();

    for (const day of forecast.days) {
      const hourlyData = day.hourly || day.weather_forecasts || [];
      if (!Array.isArray(hourlyData) || hourlyData.length === 0) continue;
      hourlyData.forEach((h) => {
        if (h?.timestamp) {
          candidates.push(h);
        }
      });
    }

    // Sort by time ascending
    candidates.sort((a, b) => {
      const ta = new Date(a.timestamp).getTime();
      const tb = new Date(b.timestamp).getTime();
      return ta - tb;
    });

    // Pick future-first (>= now), then fallback with earliest to ensure 3 points if available
    const future = candidates.filter((c) => new Date(c.timestamp) >= now);
    const picked = future.slice(0, 3);
    if (picked.length < 3) {
      const remaining = candidates
        .filter((c) => !picked.includes(c))
        .slice(0, 3 - picked.length);
      picked.push(...remaining);
    }

    return picked.slice(0, 3);
  }
}

export const weatherService = new WeatherService();
