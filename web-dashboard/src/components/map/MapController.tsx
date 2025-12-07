// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import type { LatLngBoundsExpression } from 'leaflet';

interface MapControllerProps {
  center?: [number, number];
  zoom?: number;
  bounds?: [[number, number], [number, number]] | null;
}

/**
 * Component to programmatically control the map view
 * Must be used inside a MapContainer
 */
export default function MapController({ center, zoom, bounds }: MapControllerProps) {
  const map = useMap();

  useEffect(() => {
    if (bounds) {
      // Fit to bounds with padding
      map.fitBounds(bounds as LatLngBoundsExpression, {
        padding: [50, 50],
        maxZoom: 16,
        animate: true,
        duration: 0.5,
      });
    } else if (center && zoom) {
      map.setView(center, zoom, { animate: true, duration: 0.5 });
    }
  }, [map, bounds, center, zoom]);

  return null;
}
