// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useCachedImage } from '@/lib/image-cache';
import { Image as ImageIcon } from 'lucide-react';

interface CachedImageProps {
  src: string;
  alt: string;
  className?: string;
  fallbackClassName?: string;
  fallbackIcon?: React.ReactNode;
}

export function CachedImage({ 
  src, 
  alt, 
  className = '', 
  fallbackClassName = '',
  fallbackIcon
}: CachedImageProps) {
  const cachedUrl = useCachedImage(src);

  if (!cachedUrl) {
    return (
      <div className={`${fallbackClassName} bg-muted flex items-center justify-center`}>
        <div className="animate-pulse">
          {fallbackIcon || <ImageIcon className="h-8 w-8 text-muted-foreground/50" />}
        </div>
      </div>
    );
  }

  return (
    <img
      src={cachedUrl}
      alt={alt}
      className={className}
      loading="lazy"
      onError={(e) => {
        // Fallback to SVG placeholder on error
        (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect fill="%23f0f0f0" width="100" height="100"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-size="12">No Image</text></svg>';
      }}
    />
  );
}
