// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Image Optimization Utilities
 * Helpers for lazy loading and optimizing image display
 */

/**
 * Create thumbnail URL from image URL (if supported by backend)
 */
export const getThumbnailUrl = (url: string, width: number = 300): string => {
  // If using cloud storage with image transformation support
  // You can append query parameters for resizing
  // Example: Cloudinary, imgix, etc.
  
  // For now, return original URL
  // TODO: Implement thumbnail generation on backend
  return url;
};

/**
 * Lazy load image with loading placeholder
 */
export const useLazyImage = (src: string) => {
  const [imageSrc, setImageSrc] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const img = new Image();
    img.src = src;
    
    img.onload = () => {
      setImageSrc(src);
      setIsLoading(false);
    };

    img.onerror = () => {
      setIsLoading(false);
    };
  }, [src]);

  return { imageSrc, isLoading };
};

/**
 * Intersection Observer hook for lazy loading
 */
export const useIntersectionObserver = (
  elementRef: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
): boolean => {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect();
      }
    }, options);

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [elementRef, options]);

  return isVisible;
};

/**
 * Optimize media array - limit to first N items
 */
export const limitMediaItems = <T extends { uri: string; type: string }>(
  media: T[],
  limit: number = 3
): T[] => {
  return media.slice(0, limit);
};

/**
 * Check if media item is image
 */
export const isImage = (media: { type: string }): boolean => {
  return media.type === 'image';
};

/**
 * Check if media item is video
 */
export const isVideo = (media: { type: string }): boolean => {
  return media.type === 'video';
};

/**
 * Get media count summary
 */
export const getMediaSummary = (media: { type: string }[]): {
  images: number;
  videos: number;
  total: number;
} => {
  const images = media.filter(isImage).length;
  const videos = media.filter(isVideo).length;
  
  return {
    images,
    videos,
    total: media.length,
  };
};

import React from 'react';
