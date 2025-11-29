// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon.src,
  shadowUrl: iconShadow.src,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface CityMapProps {
  center?: [number, number];
  zoom?: number;
  onMapReady?: (map: L.Map) => void;
}

export default function CityMap({ 
  center = [21.0285, 105.8542], // Hanoi coordinates
  zoom = 13,
  onMapReady 
}: CityMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [currentLayer, setCurrentLayer] = useState<'streets' | 'satellite'>('streets');

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current, {
      center,
      zoom,
      zoomControl: false,
      attributionControl: true,
    });

    // Street map layer (OpenStreetMap)
    const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    });

    // Satellite layer (Esri World Imagery)
    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri',
      maxZoom: 19,
    });

    // Satellite labels overlay
    const labelsLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://carto.com/">CARTO</a>',
      maxZoom: 19,
      pane: 'shadowPane'
    });

    // Start with street map
    streetLayer.addTo(map);

    // Custom zoom control (bottom right)
    L.control.zoom({
      position: 'bottomright'
    }).addTo(map);

    // Add sample markers for demonstration
    const hanoiLandmarks = [
      { coords: [21.0285, 105.8542] as [number, number], name: 'Hồ Hoàn Kiếm', type: 'landmark' },
      { coords: [21.0245, 105.8412] as [number, number], name: 'Văn Miếu', type: 'heritage' },
      { coords: [21.0368, 105.8345] as [number, number], name: 'Lăng Chủ tịch Hồ Chí Minh', type: 'heritage' },
      { coords: [21.0277, 105.8342] as [number, number], name: 'Chùa Một Cột', type: 'heritage' },
    ];

    hanoiLandmarks.forEach(landmark => {
      const markerColor = landmark.type === 'heritage' ? '#16A34A' : '#3B82F6';
      
      const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `
          <div style="
            width: 32px;
            height: 32px;
            background-color: ${markerColor};
            border: 3px solid white;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ">
            <div style="
              width: 100%;
              height: 100%;
              display: flex;
              align-items: center;
              justify-content: center;
              transform: rotate(45deg);
              color: white;
              font-size: 16px;
            ">📍</div>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
      });

      L.marker(landmark.coords, { icon: customIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family: Inter, sans-serif; padding: 8px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #0F172A;">
              ${landmark.name}
            </h3>
            <p style="margin: 0; font-size: 14px; color: #64748B;">
              Loại: ${landmark.type === 'heritage' ? 'Di sản' : 'Địa danh'}
            </p>
          </div>
        `);
    });

    mapInstanceRef.current = map;

    // Store layers for switching
    (window as any).__mapLayers = {
      street: streetLayer,
      satellite: satelliteLayer,
      labels: labelsLayer,
    };

    if (onMapReady) {
      onMapReady(map);
    }

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [center, zoom, onMapReady]);

  const switchMapLayer = (layerType: 'streets' | 'satellite') => {
    if (!mapInstanceRef.current) return;

    const layers = (window as any).__mapLayers;
    if (!layers) return;

    const map = mapInstanceRef.current;

    if (layerType === 'satellite') {
      map.removeLayer(layers.street);
      layers.satellite.addTo(map);
      layers.labels.addTo(map);
    } else {
      map.removeLayer(layers.satellite);
      map.removeLayer(layers.labels);
      layers.street.addTo(map);
    }

    setCurrentLayer(layerType);
  };

  return (
    <div className="relative h-full w-full">
      <div ref={mapRef} className="h-full w-full rounded-xl overflow-hidden" />
      
      {/* Map Layer Switcher */}
      <div className="absolute top-4 right-4 z-[1000] flex gap-2">
        <button
          onClick={() => switchMapLayer('streets')}
          className={`
            px-4 py-2 rounded-lg font-medium text-sm transition-all
            ${currentLayer === 'streets' 
              ? 'bg-accent text-white shadow-lg' 
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
            }
          `}
        >
          🗺️ Đường phố
        </button>
        <button
          onClick={() => switchMapLayer('satellite')}
          className={`
            px-4 py-2 rounded-lg font-medium text-sm transition-all
            ${currentLayer === 'satellite' 
              ? 'bg-accent text-white shadow-lg' 
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
            }
          `}
        >
          🛰️ Vệ tinh
        </button>
      </div>

      {/* Map Info Panel */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 max-w-xs">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          📊 Thông tin bản đồ
        </h3>
        <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-accent"></span>
            <span>Di sản văn hóa</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-blue-500"></span>
            <span>Địa danh nổi bật</span>
          </div>
        </div>
      </div>

      {/* Custom Styles for Dark Mode */}
      <style jsx global>{`
        .leaflet-container {
          font-family: 'Inter', sans-serif;
        }
        
        .dark .leaflet-tile {
          filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7);
        }

        .dark .leaflet-control-zoom a {
          background-color: #1F2937 !important;
          color: #F9FAFB !important;
          border-color: #374151 !important;
        }

        .dark .leaflet-control-zoom a:hover {
          background-color: #374151 !important;
        }

        .dark .leaflet-popup-content-wrapper {
          background-color: #1F2937;
          color: #F9FAFB;
        }

        .dark .leaflet-popup-tip {
          background-color: #1F2937;
        }

        .leaflet-control-zoom a {
          width: 36px !important;
          height: 36px !important;
          line-height: 36px !important;
          font-size: 20px !important;
          border-radius: 8px !important;
          margin: 4px !important;
        }

        .leaflet-popup-content-wrapper {
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .custom-marker {
          background: transparent;
          border: none;
        }
      `}</style>
    </div>
  );
}
