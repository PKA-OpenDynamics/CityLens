// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Leaflet React Wrapper Components
 * 
 * This module provides React components that wrap Leaflet (BSD-2-Clause license)
 * for use in React/Next.js applications.
 * 
 * Using Leaflet directly ensures full open-source license compliance.
 * Leaflet License: BSD-2-Clause (https://github.com/Leaflet/Leaflet/blob/main/LICENSE)
 */

'use client';

import React, { createContext, useContext, useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import ReactDOM from 'react-dom/client';

// Fix Leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Context for map instance
const MapContext = createContext<L.Map | null>(null);

// Hook to get map instance
export function useMap() {
  const map = useContext(MapContext);
  if (!map) {
    throw new Error('useMap must be used within a MapContainer');
  }
  return map;
}

// MapContainer Component
interface MapContainerProps {
  center: [number, number];
  zoom: number;
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  zoomControl?: boolean;
  attributionControl?: boolean;
  scrollWheelZoom?: boolean;
}

export const MapContainer = forwardRef<L.Map, MapContainerProps>(
  (
    {
      center,
      zoom,
      className,
      style,
      children,
      zoomControl = true,
      attributionControl = true,
      scrollWheelZoom = true,
    },
    ref
  ) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [map, setMap] = useState<L.Map | null>(null);

    useImperativeHandle(ref, () => map as L.Map, [map]);

    useEffect(() => {
      if (!containerRef.current || map) return;

      const newMap = L.map(containerRef.current, {
        center,
        zoom,
        zoomControl,
        attributionControl,
        scrollWheelZoom,
      });

      setMap(newMap);

      return () => {
        newMap.remove();
      };
    }, []);

    return (
      <div ref={containerRef} className={className} style={style}>
        {map && <MapContext.Provider value={map}>{children}</MapContext.Provider>}
      </div>
    );
  }
);

MapContainer.displayName = 'MapContainer';

// TileLayer Component
interface TileLayerProps {
  url: string;
  attribution?: string;
  maxZoom?: number;
  zIndex?: number;
  opacity?: number;
}

export function TileLayer({ url, attribution, maxZoom = 19, zIndex = 1, opacity = 1 }: TileLayerProps) {
  const map = useMap();

  useEffect(() => {
    const tileLayer = L.tileLayer(url, {
      attribution,
      maxZoom,
      zIndex,
      opacity,
    }).addTo(map);

    return () => {
      map.removeLayer(tileLayer);
    };
  }, [map, url, attribution, maxZoom, zIndex, opacity]);

  return null;
}

// GeoJSON Component
interface GeoJSONProps {
  data: any;
  style?: L.PathOptions | ((feature: any) => L.PathOptions);
  onEachFeature?: (feature: any, layer: L.Layer) => void;
}

export function GeoJSON({ data, style, onEachFeature }: GeoJSONProps) {
  const map = useMap();

  useEffect(() => {
    if (!data) return;

    const geoJsonLayer = L.geoJSON(data, {
      style: style as any,
      onEachFeature,
    }).addTo(map);

    return () => {
      map.removeLayer(geoJsonLayer);
    };
  }, [map, data, style, onEachFeature]);

  return null;
}

// Marker Component
interface MarkerProps {
  position: [number, number];
  icon?: L.Icon | L.DivIcon;
  children?: React.ReactNode;
}

export function Marker({ position, icon, children }: MarkerProps) {
  const map = useMap();
  const markerRef = useRef<L.Marker | null>(null);
  const popupRef = useRef<L.Popup | null>(null);
  const popupRootRef = useRef<ReactDOM.Root | null>(null);

  useEffect(() => {
    const marker = L.marker(position, { icon }).addTo(map);
    markerRef.current = marker;

    if (children) {
      const popup = L.popup();
      popupRef.current = popup;
      marker.bindPopup(popup);

      marker.on('popupopen', () => {
        const popupElement = popup.getElement();
        if (popupElement) {
          const content = popupElement.querySelector('.leaflet-popup-content');
          if (content) {
            if (!popupRootRef.current) {
              popupRootRef.current = ReactDOM.createRoot(content);
            }
            popupRootRef.current.render(<>{children}</>);
          }
        }
      });
    }

    return () => {
      if (popupRootRef.current) {
        popupRootRef.current.unmount();
        popupRootRef.current = null;
      }
      map.removeLayer(marker);
    };
  }, [map, position, icon, children]);

  return null;
}

// Popup Component (for use inside Marker)
interface PopupProps {
  closeButton?: boolean;
  maxWidth?: number;
  minWidth?: number;
  className?: string;
  children?: React.ReactNode;
}

export function Popup({ children }: PopupProps) {
  return <>{children}</>;
}

// CircleMarker Component
interface CircleMarkerProps {
  center: [number, number];
  radius?: number;
  pathOptions?: L.PathOptions;
  children?: React.ReactNode;
}

export function CircleMarker({ center, radius = 10, pathOptions, children }: CircleMarkerProps) {
  const map = useMap();
  const circleRef = useRef<L.CircleMarker | null>(null);
  const popupRef = useRef<L.Popup | null>(null);
  const popupRootRef = useRef<ReactDOM.Root | null>(null);

  useEffect(() => {
    const circle = L.circleMarker(center, {
      radius,
      ...pathOptions,
    }).addTo(map);
    circleRef.current = circle;

    if (children) {
      const popup = L.popup();
      popupRef.current = popup;
      circle.bindPopup(popup);

      circle.on('popupopen', () => {
        const popupElement = popup.getElement();
        if (popupElement) {
          const content = popupElement.querySelector('.leaflet-popup-content');
          if (content) {
            if (!popupRootRef.current) {
              popupRootRef.current = ReactDOM.createRoot(content);
            }
            popupRootRef.current.render(<>{children}</>);
          }
        }
      });
    }

    return () => {
      if (popupRootRef.current) {
        popupRootRef.current.unmount();
        popupRootRef.current = null;
      }
      map.removeLayer(circle);
    };
  }, [map, center, radius, pathOptions, children]);

  return null;
}

// Export all components
export { MapContext };
