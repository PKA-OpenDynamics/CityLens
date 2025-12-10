// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Image Cache Service
 * Provides client-side image caching for better performance
 */

class ImageCacheService {
  private cache: Map<string, string> = new Map();
  private readonly CACHE_PREFIX = 'citylens_img_';
  // Reserved for future use:
  // private readonly MAX_CACHE_SIZE = 100; // Maximum images before cleanup
  // private readonly CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

  constructor() {
    // Load cache from localStorage on initialization
    this.loadCacheFromStorage();
  }

  /**
   * Load cached images from localStorage
   */
  private loadCacheFromStorage() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.CACHE_PREFIX)) {
          const data = localStorage.getItem(key);
          if (data) {
            try {
              const parsed = JSON.parse(data);
              const now = Date.now();
              
              // Check if cache is still valid
              if (parsed.expiry && parsed.expiry > now) {
                const url = key.replace(this.CACHE_PREFIX, '');
                this.cache.set(url, parsed.data);
              } else {
                // Remove expired cache
                localStorage.removeItem(key);
              }
            } catch {
              localStorage.removeItem(key);
            }
          }
        }
      });
    } catch (error) {
      console.warn('Failed to load image cache from storage:', error);
    }
  }

  /**
   * Get cache key for URL
   */
  private getCacheKey(url: string): string {
    return `${this.CACHE_PREFIX}${url}`;
  }

  /**
   * Get cached image or fetch and cache it
   */
  async getImage(url: string): Promise<string> {
    // Check memory cache first
    const cached = this.cache.get(url);
    if (cached) {
      return cached;
    }

    // Check localStorage
    try {
      const key = this.getCacheKey(url);
      const stored = localStorage.getItem(key);
      
      if (stored) {
        const parsed = JSON.parse(stored);
        const now = Date.now();
        
        if (parsed.expiry && parsed.expiry > now) {
          this.cache.set(url, parsed.data);
          return parsed.data;
        } else {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.warn('Failed to get cached image:', error);
    }

    // Not in cache, return original URL
    // The browser will handle caching via HTTP headers
    return url;
  }

  /**
   * Preload and cache an image
   */
  async preloadImage(url: string): Promise<void> {
    try {
      // Check if already cached
      if (this.cache.has(url)) {
        return;
      }

      // For now, just add to cache as-is
      // Browser will handle the actual caching via HTTP headers
      this.cache.set(url, url);

      // Optionally save to localStorage (for very important images)
      // We skip this by default to avoid bloating localStorage
      
    } catch (error) {
      console.warn('Failed to preload image:', error);
    }
  }

  /**
   * Preload multiple images
   */
  async preloadImages(urls: string[]): Promise<void> {
    await Promise.all(urls.map(url => this.preloadImage(url)));
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
    
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.CACHE_PREFIX)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('Failed to clear image cache:', error);
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): {
    memorySize: number;
    storageSize: number;
  } {
    let storageSize = 0;
    
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.CACHE_PREFIX)) {
          storageSize++;
        }
      });
    } catch (error) {
      // Ignore
    }

    return {
      memorySize: this.cache.size,
      storageSize,
    };
  }
}

// Export singleton instance
export const imageCacheService = new ImageCacheService();

/**
 * React hook for image caching
 */
export const useCachedImage = (url: string | undefined) => {
  const [cachedUrl, setCachedUrl] = React.useState<string | undefined>(url);

  React.useEffect(() => {
    if (!url) {
      setCachedUrl(undefined);
      return;
    }

    imageCacheService.getImage(url).then(cached => {
      setCachedUrl(cached);
    });
  }, [url]);

  return cachedUrl;
};

/**
 * Preload images for better UX
 */
export const preloadImages = (urls: string[]) => {
  imageCacheService.preloadImages(urls);
};

import React from 'react';
