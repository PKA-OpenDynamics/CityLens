const normalizeApiBase = (base: string): string => {
  if (!base) return '';
  if (base.endsWith('/')) return base.slice(0, -1);
  return base;
};

const API_BASE = normalizeApiBase(
  (typeof process !== 'undefined' && (process.env as any)?.EXPO_PUBLIC_API_BASE_URL) ||
    (typeof process !== 'undefined' && (process.env as any)?.WEATHER_API_BASE_URL) ||
    'https://rooms-tools-kirk-nelson.trycloudflare.com/api/v1'
);

export type AlertItem = {
  _id: string;
  type?: string;
  severity?: string;
  title: string;
  description?: string;
  ward?: string;
  recommendation?: string;
  impact?: string;
  affectedPopulation?: string;
  isAIGenerated?: boolean;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
};

class AlertsService {
  async list(): Promise<AlertItem[]> {
    const base = API_BASE.replace(/\/$/, '');
    const urls = [
      `${base}/app/alerts`, // Mobile app alerts endpoint
      `${base}/alerts`, // Fallback
    ];

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      try {
        const res = await fetch(url);
        if (res.status === 404) {
          // try next URL silently
          continue;
        }
        if (!res.ok) {
          // Nếu không phải URL cuối cùng, thử tiếp
          if (i < urls.length - 1) continue;
          throw new Error(`Alerts API error: ${res.status}`);
        }
        const data = await res.json();
        // Backend returns { success: true, data: [...], count: N }
        if (Array.isArray(data)) return data;
        if (Array.isArray(data?.data)) return data.data;
        if (Array.isArray(data?.items)) return data.items;
        return [];
      } catch (err) {
        // Nếu là URL cuối cùng và không phải 404, ném lỗi
        if (i === urls.length - 1) {
          console.warn('[AlertsService] All endpoints failed, returning empty array', err);
          return [];
        }
        // Tiếp tục thử URL tiếp theo
      }
    }

    return [];
  }
}

export const alertsService = new AlertsService();

