// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Simple in-memory cache for API responses
 * Reduces redundant API calls and improves performance
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class ApiCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private defaultTTL: number = 5 * 60 * 1000; // 5 minutes

  /**
   * Generate cache key from endpoint and params
   */
  private generateKey(endpoint: string, params?: Record<string, any>): string {
    if (!params) return endpoint;
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&');
    return `${endpoint}?${sortedParams}`;
  }

  /**
   * Get cached data if available and not expired
   */
  get<T>(endpoint: string, params?: Record<string, any>): T | null {
    const key = this.generateKey(endpoint, params);
    const entry = this.cache.get(key);

    if (!entry) return null;

    const now = Date.now();
    const isExpired = now - entry.timestamp > entry.ttl;

    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Set data in cache with optional TTL
   */
  set<T>(
    endpoint: string,
    data: T,
    params?: Record<string, any>,
    ttl: number = this.defaultTTL
  ): void {
    const key = this.generateKey(endpoint, params);
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * Invalidate specific cache entry
   */
  invalidate(endpoint: string, params?: Record<string, any>): void {
    const key = this.generateKey(endpoint, params);
    this.cache.delete(key);
  }

  /**
   * Invalidate all cache entries matching pattern
   */
  invalidatePattern(pattern: RegExp): void {
    const keys = Array.from(this.cache.keys());
    keys.forEach(key => {
      if (pattern.test(key)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number;
    entries: string[];
  } {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys()),
    };
  }
}

// Export singleton instance
export const apiCache = new ApiCache();

// Export hook for React components
export const useApiCache = () => {
  return {
    get: apiCache.get.bind(apiCache),
    set: apiCache.set.bind(apiCache),
    invalidate: apiCache.invalidate.bind(apiCache),
    invalidatePattern: apiCache.invalidatePattern.bind(apiCache),
    clear: apiCache.clear.bind(apiCache),
    getStats: apiCache.getStats.bind(apiCache),
  };
};
