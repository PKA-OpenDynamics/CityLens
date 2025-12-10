// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import dynamic from 'next/dynamic';
import { 
  RefreshCw, PanelRightOpen, PanelRightClose,
  Map as MapIcon, Satellite, Camera
} from 'lucide-react';
import { 
  geographicApi, 
  geographicStatsApi,
  type GeoJSONFeatureCollection,
  type GeographicStatistics,
  type BoundaryDetails
} from '@/lib/api';
import { cn } from '@/lib/utils';
import { BoundarySelector, IntegratedDataPanel } from '@/components/geographic';

// Dynamic imports for Leaflet (no SSR)
const MapContainer = dynamic(
  () => import('react-leaflet').then(mod => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then(mod => mod.TileLayer),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import('react-leaflet').then(mod => mod.GeoJSON),
  { ssr: false }
);
const Popup = dynamic(
  () => import('react-leaflet').then(mod => mod.Popup),
  { ssr: false }
);
const CircleMarker = dynamic(
  () => import('react-leaflet').then(mod => mod.CircleMarker),
  { ssr: false }
);
const Marker = dynamic(
  () => import('react-leaflet').then(mod => mod.Marker),
  { ssr: false }
);

// Traffic Camera components
import { TRAFFIC_CAMERAS, TrafficCameraPopup, type TrafficCamera } from '@/components/map/TrafficCamera';

// Camera Marker component for use with react-leaflet
const CameraMarkerWithPopup = dynamic(
  () => Promise.resolve(({ camera }: { camera: TrafficCamera }) => {
    const L = typeof window !== 'undefined' ? require('leaflet') : null;
    const { Marker: LeafletMarker, Popup: LeafletPopup } = require('react-leaflet');
    
    if (!L) return null;
    
    const cameraIcon = L.divIcon({
      className: 'camera-marker',
      html: `
        <div class="relative flex flex-col items-center">
          <div class="w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
            camera.status === 'online' ? 'bg-green-600' : 
            camera.status === 'demo' ? 'bg-yellow-600' : 'bg-red-600'
          } border-2 border-white">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <circle cx="12" cy="13" r="3"/>
            </svg>
          </div>
          <span class="absolute -top-1 -right-1 w-3 h-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
        </div>
      `,
      iconSize: [44, 44],
      iconAnchor: [22, 44],
      popupAnchor: [0, -44],
    });
    
    return (
      <LeafletMarker 
        position={camera.location}
        icon={cameraIcon}
      >
        <LeafletPopup
          closeButton={true}
          maxWidth={350}
          minWidth={320}
          className="camera-popup"
        >
          <TrafficCameraPopup camera={camera} />
        </LeafletPopup>
      </LeafletMarker>
    );
  }),
  { ssr: false }
);

// MapController component - controls map view programmatically
const MapController = dynamic(
  () => import('react-leaflet').then(mod => {
    const { useMap } = mod;
    const { useEffect } = require('react');
    
    // Return a component that uses useMap
    return {
      default: function MapControllerInner({ 
        bounds 
      }: { 
        center?: [number, number]; 
        zoom?: number; 
        bounds?: [[number, number], [number, number]] | null;
      }) {
        const map = useMap();
        
        useEffect(() => {
          // Fit to bounds when bounds change
          if (bounds) {
            map.fitBounds(bounds, {
              padding: [50, 50],
              maxZoom: 16,
              animate: true,
              duration: 0.5,
            });
          }
        }, [map, bounds]);
        
        return null;
      }
    };
  }),
  { ssr: false }
);

// Hanoi center coordinates
const HANOI_CENTER: [number, number] = [21.028511, 105.804817];
const DEFAULT_ZOOM = 11;
const SELECTED_ZOOM = 14;

// Map tile layers
const MAP_LAYERS = {
  satellite: {
    name: 'Vệ tinh',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
  },
  osm: {
    name: 'Bản đồ',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  },
  hybrid: {
    name: 'Hybrid',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri',
  },
};

// Layer visibility state type
interface LayerVisibility {
  boundaries: boolean;
  districts: boolean;
  pois: boolean;
  traffic: boolean;
  cameras: boolean;
}

// TomTom Traffic Flow layer (requires API key from environment)
const TOMTOM_TRAFFIC_LAYER = {
  // Traffic flow tiles - shows traffic speed as colors on roads
  url: `https://api.tomtom.com/traffic/map/4/tile/flow/relative0/{z}/{x}/{y}.png?key=${process.env.NEXT_PUBLIC_TOMTOM_API_KEY || ''}`,
  attribution: '&copy; TomTom Traffic',
};

type MapLayerType = 'satellite' | 'osm' | 'hybrid';

// POI Configuration - colors, icons, Vietnamese names
const POI_CONFIG: Record<string, { 
  color: string; 
  name: string; 
  emoji: string;
  priority: number;
}> = {
  // Healthcare - Red
  hospital: { color: '#dc2626', name: 'Bệnh viện', emoji: '🏥', priority: 1 },
  clinic: { color: '#ef4444', name: 'Phòng khám', emoji: '🏥', priority: 2 },
  pharmacy: { color: '#f87171', name: 'Nhà thuốc', emoji: '💊', priority: 3 },
  doctors: { color: '#ef4444', name: 'Phòng khám', emoji: '👨‍⚕️', priority: 2 },
  dentist: { color: '#ef4444', name: 'Nha khoa', emoji: '🦷', priority: 3 },
  
  // Education - Indigo
  school: { color: '#4f46e5', name: 'Trường học', emoji: '🏫', priority: 1 },
  kindergarten: { color: '#6366f1', name: 'Mầm non', emoji: '👶', priority: 2 },
  university: { color: '#4338ca', name: 'Đại học', emoji: '🎓', priority: 1 },
  college: { color: '#4f46e5', name: 'Cao đẳng', emoji: '🎓', priority: 2 },
  library: { color: '#6366f1', name: 'Thư viện', emoji: '📚', priority: 3 },
  
  // Finance - Emerald
  bank: { color: '#059669', name: 'Ngân hàng', emoji: '🏦', priority: 1 },
  atm: { color: '#10b981', name: 'Cây ATM', emoji: '💳', priority: 3 },
  
  // Shopping - Orange
  supermarket: { color: '#ea580c', name: 'Siêu thị', emoji: '🛒', priority: 1 },
  marketplace: { color: '#f97316', name: 'Chợ', emoji: '🏪', priority: 1 },
  mall: { color: '#ea580c', name: 'TTTM', emoji: '🏬', priority: 1 },
  convenience: { color: '#fb923c', name: 'Tiện lợi', emoji: '🏪', priority: 3 },
  department_store: { color: '#f97316', name: 'Bách hóa', emoji: '🏬', priority: 2 },
  
  // Food & Drink - Amber
  restaurant: { color: '#d97706', name: 'Nhà hàng', emoji: '🍽️', priority: 2 },
  cafe: { color: '#f59e0b', name: 'Cà phê', emoji: '☕', priority: 3 },
  fast_food: { color: '#fbbf24', name: 'Ăn nhanh', emoji: '🍔', priority: 3 },
  bar: { color: '#d97706', name: 'Bar', emoji: '🍺', priority: 4 },
  
  // Government - Slate
  police: { color: '#475569', name: 'Công an', emoji: '👮', priority: 1 },
  fire_station: { color: '#dc2626', name: 'Cứu hỏa', emoji: '🚒', priority: 1 },
  post_office: { color: '#64748b', name: 'Bưu điện', emoji: '📮', priority: 2 },
  townhall: { color: '#475569', name: 'UBND', emoji: '🏛️', priority: 1 },
  
  // Transport - Cyan
  fuel: { color: '#0891b2', name: 'Trạm xăng', emoji: '⛽', priority: 2 },
  parking: { color: '#06b6d4', name: 'Bãi đỗ xe', emoji: '🅿️', priority: 3 },
  bus_station: { color: '#0891b2', name: 'Bến xe', emoji: '🚌', priority: 2 },
  charging_station: { color: '#22d3ee', name: 'Trạm sạc', emoji: '🔌', priority: 3 },
  
  // Religion - Yellow
  place_of_worship: { color: '#ca8a04', name: 'Tôn giáo', emoji: '⛪', priority: 3 },
  
  // Tourism - Purple
  hotel: { color: '#7c3aed', name: 'Khách sạn', emoji: '🏨', priority: 2 },
  museum: { color: '#8b5cf6', name: 'Bảo tàng', emoji: '🏛️', priority: 2 },
  attraction: { color: '#a78bfa', name: 'Điểm tham quan', emoji: '📸', priority: 2 },
  
  // Leisure - Green
  park: { color: '#16a34a', name: 'Công viên', emoji: '🌳', priority: 2 },
  sports_centre: { color: '#22c55e', name: 'Thể thao', emoji: '🏃', priority: 3 },
  cinema: { color: '#84cc16', name: 'Rạp phim', emoji: '🎬', priority: 3 },
  
  // Default
  default: { color: '#6b7280', name: 'Địa điểm', emoji: '📍', priority: 5 },
};

// Get POI config by subcategory or category
function getPOIConfig(subcategory: string | null, category: string): typeof POI_CONFIG[string] {
  if (subcategory && POI_CONFIG[subcategory]) {
    return POI_CONFIG[subcategory];
  }
  // Try category-based mapping
  if (category === 'healthcare') return POI_CONFIG.hospital;
  if (category === 'education') return POI_CONFIG.school;
  if (category === 'finance') return POI_CONFIG.bank;
  if (category === 'shop') return POI_CONFIG.convenience;
  if (category === 'tourism') return POI_CONFIG.hotel;
  if (category === 'leisure') return POI_CONFIG.park;
  return POI_CONFIG.default;
}

// Vietnamese subcategory names
const SUBCATEGORY_NAMES: Record<string, string> = {
  hospital: 'Bệnh viện',
  clinic: 'Phòng khám',
  pharmacy: 'Nhà thuốc',
  doctors: 'Phòng khám bác sĩ',
  dentist: 'Nha khoa',
  school: 'Trường học',
  kindergarten: 'Trường mầm non',
  university: 'Đại học',
  college: 'Cao đẳng',
  library: 'Thư viện',
  bank: 'Ngân hàng',
  atm: 'Cây ATM',
  supermarket: 'Siêu thị',
  marketplace: 'Chợ',
  mall: 'Trung tâm thương mại',
  convenience: 'Cửa hàng tiện lợi',
  department_store: 'Cửa hàng bách hóa',
  restaurant: 'Nhà hàng',
  cafe: 'Quán cà phê',
  fast_food: 'Đồ ăn nhanh',
  bar: 'Quán bar',
  police: 'Công an',
  fire_station: 'Trạm cứu hỏa',
  post_office: 'Bưu điện',
  townhall: 'UBND',
  fuel: 'Trạm xăng',
  parking: 'Bãi đỗ xe',
  bus_station: 'Bến xe buýt',
  charging_station: 'Trạm sạc điện',
  place_of_worship: 'Nơi thờ cúng',
  hotel: 'Khách sạn',
  museum: 'Bảo tàng',
  attraction: 'Điểm tham quan',
  park: 'Công viên',
  sports_centre: 'Trung tâm thể thao',
  cinema: 'Rạp chiếu phim',
  clothes: 'Quần áo',
  mobile_phone: 'Điện thoại',
  electronics: 'Điện tử',
  furniture: 'Nội thất',
  bakery: 'Tiệm bánh',
  hairdresser: 'Làm tóc',
  beauty: 'Mỹ phẩm',
};

export default function GeographicPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [mounted, setMounted] = useState(false);
  
  // Data states
  const [statistics, setStatistics] = useState<GeographicStatistics | null>(null);
  const [hanoiBoundary, setHanoiBoundary] = useState<any | null>(null);
  const [hanoiInfo, setHanoiInfo] = useState<{ num_wards: number; area_km2: number } | null>(null);
  const [districtsGeoJSON, setDistrictsGeoJSON] = useState<GeoJSONFeatureCollection | null>(null);
  
  // Selection states
  const [selectedBoundaryIds, setSelectedBoundaryIds] = useState<number[]>([]);
  const [activeBoundaryId, setActiveBoundaryId] = useState<number | null>(null);
  const [activeDetails, setActiveDetails] = useState<BoundaryDetails | null>(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(true);
  
  // Map states
  const [mapCenter, setMapCenter] = useState<[number, number]>(HANOI_CENTER);
  const [mapZoom, setMapZoom] = useState(DEFAULT_ZOOM);
  const [mapBounds, setMapBounds] = useState<[[number, number], [number, number]] | null>(null);
  const [activeMapLayer, setActiveMapLayer] = useState<MapLayerType>('satellite');
  
  // Layer visibility
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    boundaries: true,
    districts: true,
    pois: true,
    traffic: false,
    cameras: true,
  });
  
  // Refs
  const mapRef = useRef<any>(null);

  // Client-side only
  useEffect(() => {
    setMounted(true);
  }, []);

  // Fetch data
  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const [statsResult, boundariesResult, districtsResult] = await Promise.allSettled([
        geographicStatsApi.getStatistics(),
        geographicApi.getHanoiUnionBoundary({ simplify_tolerance: 0.0005 }),
        geographicApi.getBoundariesGeoJSON({ admin_level: 6 })
      ]);

      if (statsResult.status === 'fulfilled') {
        setStatistics(statsResult.value);
      }
      if (boundariesResult.status === 'fulfilled') {
        const unionData = boundariesResult.value;
        setHanoiBoundary({
          type: 'FeatureCollection',
          features: [unionData]
        });
        setHanoiInfo({
          num_wards: unionData.properties.num_wards,
          area_km2: unionData.properties.area_km2
        });
      }
      if (districtsResult.status === 'fulfilled') {
        setDistrictsGeoJSON(districtsResult.value);
      }
    } catch (error) {
      console.error('Error fetching geographic data:', error);
    }

    setLoading(false);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Update active boundary when selection changes
  useEffect(() => {
    if (selectedBoundaryIds.length > 0) {
      setActiveBoundaryId(selectedBoundaryIds[selectedBoundaryIds.length - 1]);
    } else {
      setActiveBoundaryId(null);
      setActiveDetails(null);
    }
  }, [selectedBoundaryIds]);

  // Fetch details and zoom to boundary when active changes
  useEffect(() => {
    if (!activeBoundaryId) {
      setActiveDetails(null);
      return;
    }

    const fetchDetailsAndZoom = async () => {
      try {
        const details = await geographicApi.getBoundaryDetails(activeBoundaryId, true);
        setActiveDetails(details);
        
        // Zoom to boundary
        if (details.boundary.geometry) {
          const geometry = details.boundary.geometry;
          let bounds: [[number, number], [number, number]] | null = null;
          
          if (geometry.type === 'Polygon') {
            const coords = (geometry as any).coordinates[0];
            let minLat = Infinity, maxLat = -Infinity;
            let minLng = Infinity, maxLng = -Infinity;
            
            coords.forEach((coord: [number, number]) => {
              const [lng, lat] = coord;
              minLat = Math.min(minLat, lat);
              maxLat = Math.max(maxLat, lat);
              minLng = Math.min(minLng, lng);
              maxLng = Math.max(maxLng, lng);
            });
            
            bounds = [[minLat, minLng], [maxLat, maxLng]];
          } else if (geometry.type === 'MultiPolygon') {
            let minLat = Infinity, maxLat = -Infinity;
            let minLng = Infinity, maxLng = -Infinity;
            
            (geometry as any).coordinates.forEach((polygon: any) => {
              polygon[0].forEach((coord: [number, number]) => {
                const [lng, lat] = coord;
                minLat = Math.min(minLat, lat);
                maxLat = Math.max(maxLat, lat);
                minLng = Math.min(minLng, lng);
                maxLng = Math.max(maxLng, lng);
              });
            });
            
            bounds = [[minLat, minLng], [maxLat, maxLng]];
          }
          
          if (bounds) {
            setMapBounds(bounds);
          }
        } else {
          // Fallback to center point
          setMapCenter([details.boundary.center.lat, details.boundary.center.lng]);
          setMapZoom(SELECTED_ZOOM);
        }
      } catch (error) {
        console.error('Error fetching boundary details:', error);
      }
    };

    fetchDetailsAndZoom();
  }, [activeBoundaryId]);

  // GeoJSON styles
  const boundaryStyle = useMemo(() => ({
    color: '#dc2626',
    weight: 3,
    opacity: 1,
    fillColor: '#dc2626',
    fillOpacity: 0.02
  }), []);

  // Dynamic style based on selection
  const getDistrictStyle = useCallback((feature: any) => {
    const isSelected = selectedBoundaryIds.includes(feature.id);
    const isActive = feature.id === activeBoundaryId;
    
    if (isActive) {
      return {
        color: '#16a34a',
        weight: 4,
        opacity: 1,
        fillColor: '#22c55e',
        fillOpacity: 0.35
      };
    }
    
    if (isSelected) {
      return {
        color: '#f59e0b',
        weight: 3,
        opacity: 1,
        fillColor: '#fbbf24',
        fillOpacity: 0.25
      };
    }
    
    return {
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.7,
      fillColor: '#3b82f6',
      fillOpacity: 0.15
    };
  }, [selectedBoundaryIds, activeBoundaryId]);

  // GeoJSON feature handlers
  const onEachBoundary = useCallback((feature: any, layer: any) => {
    if (feature.properties) {
      const name = feature.properties.name || feature.properties.name_en || 'Không xác định';
      layer.bindPopup(`
        <div class="p-2">
          <h3 class="font-semibold text-foreground">${name}</h3>
          <p class="text-sm text-muted-foreground">Ranh giới thành phố Hà Nội</p>
          <p class="text-sm">${hanoiInfo?.area_km2.toLocaleString('vi-VN')} km² • ${hanoiInfo?.num_wards} phường/xã</p>
        </div>
      `);
    }
  }, [hanoiInfo]);

  const onEachDistrict = useCallback((feature: any, layer: any) => {
    if (feature.properties) {
      const name = feature.properties.name || feature.properties.name_en || 'Không xác định';
      const id = feature.id;
      const isSelected = selectedBoundaryIds.includes(id);
      
      layer.bindPopup(`
        <div class="p-2 min-w-[180px]">
          <h3 class="font-bold text-base">${name}</h3>
          <p class="text-sm text-gray-600 mt-1">Click để ${isSelected ? 'bỏ chọn' : 'chọn và xem chi tiết'}</p>
        </div>
      `);
      
      layer.on('click', () => {
        if (selectedBoundaryIds.includes(id)) {
          setSelectedBoundaryIds(prev => prev.filter(i => i !== id));
        } else {
          setSelectedBoundaryIds(prev => [...prev, id]);
        }
      });
      
      layer.on('mouseover', () => {
        if (!selectedBoundaryIds.includes(id)) {
          layer.setStyle({ weight: 2.5, fillOpacity: 0.25 });
        }
      });
      
      layer.on('mouseout', () => {
        if (!selectedBoundaryIds.includes(id)) {
          layer.setStyle(getDistrictStyle(feature));
        }
      });
    }
  }, [selectedBoundaryIds, getDistrictStyle]);

  const toggleLayer = (layer: keyof LayerVisibility) => {
    setLayerVisibility(prev => ({ ...prev, [layer]: !prev[layer] }));
  };

  const geoJsonKey = useMemo(
    () => `wards-${selectedBoundaryIds.join('-')}-${activeBoundaryId}`,
    [selectedBoundaryIds, activeBoundaryId]
  );

  // Reset map view
  const resetMapView = useCallback(() => {
    setMapCenter(HANOI_CENTER);
    setMapZoom(DEFAULT_ZOOM);
    setMapBounds(null);
  }, []);

  // POI markers from active details
  const poiMarkers = useMemo(() => {
    if (!activeDetails || !layerVisibility.pois) return [];
    return activeDetails.statistics.top_pois.filter(poi => poi.location);
  }, [activeDetails, layerVisibility.pois]);

  return (
    <div className="space-y-4 h-full">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dữ liệu địa lý</h1>
          <p className="text-muted-foreground mt-1">
            Bản đồ ranh giới hành chính Hà Nội • {hanoiInfo?.num_wards || 126} phường/xã
          </p>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          {/* Toggle Details Panel */}
          <button
            onClick={() => setShowDetailsPanel(!showDetailsPanel)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
              "bg-card border border-border hover:bg-green-50 dark:hover:bg-green-950/20",
              showDetailsPanel ? "bg-green-50 dark:bg-green-950/30 border-green-500" : ""
            )}
            title={showDetailsPanel ? "Ẩn panel chi tiết" : "Hiện panel chi tiết"}
          >
            {showDetailsPanel ? 
              <PanelRightClose className="w-4 h-4 text-green-600 dark:text-green-500" /> : 
              <PanelRightOpen className="w-4 h-4 hover:text-green-600 dark:hover:text-green-500" />
            }
          </button>
          
          {/* Refresh Button */}
          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg",
              "bg-green-600 text-white hover:bg-green-700 transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
            <span className="hidden sm:inline">Làm mới</span>
          </button>
        </div>
      </div>

      {/* Statistics Bar */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground">Phường/Xã</p>
            <p className="text-xl font-bold text-foreground">{(statistics.administrative_boundaries?.total || 0).toLocaleString('vi-VN')}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {statistics.administrative_boundaries?.phuong || 0} phường, {statistics.administrative_boundaries?.xa || 0} xã
            </p>
          </div>
          <div className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground">Đường phố</p>
            <p className="text-xl font-bold text-foreground">{(statistics.streets?.total || 0).toLocaleString('vi-VN')}</p>
          </div>
          <div className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground">Công trình</p>
            <p className="text-xl font-bold text-foreground">{(statistics.buildings?.total || 0).toLocaleString('vi-VN')}</p>
          </div>
          <div className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground">POI</p>
            <p className="text-xl font-bold text-foreground">{(statistics.pois?.total || 0).toLocaleString('vi-VN')}</p>
          </div>
        </div>
      )}

      {/* Main Content: Controls + Map + Details Panel */}
      <div className="flex gap-4" style={{ height: 'calc(100vh - 340px)', minHeight: '500px' }}>
        
        {/* Left Sidebar - Selector & Controls */}
        <div className="w-72 flex-shrink-0 flex flex-col gap-4 overflow-visible">
          {/* Boundary Selector */}
          <div className="bg-card rounded-lg border border-border p-4 relative z-50">
            <h3 className="text-sm font-semibold text-foreground mb-3">Chọn phường/xã</h3>
            <BoundarySelector
              selectedIds={selectedBoundaryIds}
              onSelectionChange={setSelectedBoundaryIds}
              maxSelection={10}
            />
            
            {selectedBoundaryIds.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border">
                <button
                  onClick={() => {
                    setSelectedBoundaryIds([]);
                    resetMapView();
                  }}
                  className="w-full text-sm text-muted-foreground hover:text-destructive transition-colors"
                >
                  Xóa tất cả lựa chọn
                </button>
              </div>
            )}
          </div>

          {/* Map Type Selector */}
          <div className="bg-card rounded-lg border border-border p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">Loại bản đồ</h3>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setActiveMapLayer('satellite')}
                className={cn(
                  "flex flex-col items-center gap-1 p-3 rounded-lg border transition-all",
                  activeMapLayer === 'satellite' 
                    ? "border-green-500 bg-green-50 dark:bg-green-950/30 shadow-sm" 
                    : "border-border hover:bg-green-50 dark:hover:bg-green-950/20 hover:border-green-400"
                )}
              >
                <Satellite className={cn("w-5 h-5", activeMapLayer === 'satellite' ? "text-green-600" : "")} />
                <span className={cn("text-xs", activeMapLayer === 'satellite' ? "text-green-600 font-medium" : "")}>Vệ tinh</span>
              </button>
              <button
                onClick={() => setActiveMapLayer('osm')}
                className={cn(
                  "flex flex-col items-center gap-1 p-3 rounded-lg border transition-all",
                  activeMapLayer === 'osm' 
                    ? "border-green-500 bg-green-50 dark:bg-green-950/30 shadow-sm" 
                    : "border-border hover:bg-green-50 dark:hover:bg-green-950/20 hover:border-green-400"
                )}
              >
                <MapIcon className={cn("w-5 h-5", activeMapLayer === 'osm' ? "text-green-600" : "")} />
                <span className={cn("text-xs", activeMapLayer === 'osm' ? "text-green-600 font-medium" : "")}>Đường phố</span>
              </button>
            </div>
          </div>

          {/* Layer Control */}
          <div className="bg-card rounded-lg border border-border p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3">Lớp hiển thị</h3>
            <div className="space-y-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.boundaries}
                  onChange={() => toggleLayer('boundaries')}
                  className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                />
                <div>
                  <p className={`text-sm ${layerVisibility.boundaries ? 'text-green-600 font-medium' : 'text-foreground'}`}>Ranh giới Hà Nội</p>
                  <p className="text-xs text-muted-foreground">Viền đỏ</p>
                </div>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.districts}
                  onChange={() => toggleLayer('districts')}
                  className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                />
                <div>
                  <p className={`text-sm ${layerVisibility.districts ? 'text-green-600 font-medium' : 'text-foreground'}`}>Phường/Xã</p>
                  <p className="text-xs text-muted-foreground">{hanoiInfo?.num_wards || 126} đơn vị</p>
                </div>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.pois}
                  onChange={() => toggleLayer('pois')}
                  className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                />
                <div>
                  <p className={`text-sm ${layerVisibility.pois ? 'text-green-600 font-medium' : 'text-foreground'}`}>Điểm POI</p>
                  <p className="text-xs text-muted-foreground">Địa điểm quan trọng</p>
                </div>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.traffic}
                  onChange={() => toggleLayer('traffic')}
                  className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                />
                <div>
                  <p className={`text-sm ${layerVisibility.traffic ? 'text-green-600 font-medium' : 'text-foreground'}`}>Giao thông</p>
                  <p className="text-xs text-muted-foreground">Tình trạng đường (TomTom)</p>
                </div>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={layerVisibility.cameras}
                  onChange={() => toggleLayer('cameras')}
                  className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                />
                <div>
                  <p className="text-sm text-foreground flex items-center gap-1">
                    <Camera className="w-3 h-3 text-green-500" />
                    <span className={layerVisibility.cameras ? 'text-green-600 font-medium' : ''}>Camera giao thông</span>
                  </p>
                  <p className="text-xs text-muted-foreground">Xem video thực tế</p>
                </div>
              </label>
            </div>
          </div>

          {/* Legend */}
          <div className="bg-card rounded-lg border border-border p-4 flex-1 overflow-y-auto">
            <h3 className="text-sm font-semibold text-foreground mb-3">Chú thích</h3>
            
            {/* Map layers */}
            <div className="space-y-1.5 text-xs mb-4">
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 bg-red-600 rounded"></div>
                <span className="text-muted-foreground">Ranh giới HN</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-2.5 bg-blue-500/30 border border-white rounded"></div>
                <span className="text-muted-foreground">Phường/Xã</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-2.5 bg-amber-400/40 border-2 border-amber-500 rounded"></div>
                <span className="text-muted-foreground">Đã chọn</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-2.5 bg-green-500/40 border-2 border-green-600 rounded"></div>
                <span className="text-muted-foreground">Đang xem</span>
              </div>
            </div>
            
            {/* POI types */}
            <div className="border-t border-border pt-3">
              <p className="text-xs font-medium text-muted-foreground mb-2">Loại địa điểm (POI)</p>
              <div className="grid grid-cols-2 gap-1 text-[10px]">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#dc2626' }}></div>
                  <span>Y tế</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#4f46e5' }}></div>
                  <span>Giáo dục</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#059669' }}></div>
                  <span>Ngân hàng</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#ea580c' }}></div>
                  <span>Mua sắm</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#d97706' }}></div>
                  <span>Ẩm thực</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#475569' }}></div>
                  <span>Cơ quan</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#0891b2' }}></div>
                  <span>Vận tải</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#7c3aed' }}></div>
                  <span>Du lịch</span>
                </div>
              </div>
            </div>
            
            {/* Traffic Legend */}
            {layerVisibility.traffic && (
              <div className="border-t border-border pt-3 mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-2">Tình trạng giao thông</p>
                <div className="space-y-1 text-[10px]">
                  <div className="flex items-center gap-1.5">
                    <div className="w-4 h-1.5 rounded" style={{ backgroundColor: '#00E400' }}></div>
                    <span>Thông thoáng</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-4 h-1.5 rounded" style={{ backgroundColor: '#FFFF00' }}></div>
                    <span>Nhẹ</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-4 h-1.5 rounded" style={{ backgroundColor: '#FF7E00' }}></div>
                    <span>Trung bình</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-4 h-1.5 rounded" style={{ backgroundColor: '#FF0000' }}></div>
                    <span>Đông đúc</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-4 h-1.5 rounded" style={{ backgroundColor: '#7E0023' }}></div>
                    <span>Tắc nghẽn</span>
                  </div>
                </div>
              </div>
            )}

            {/* Camera Legend */}
            {layerVisibility.cameras && (
              <div className="border-t border-border pt-3 mt-3">
                <p className="text-xs font-medium text-foreground mb-2 flex items-center gap-1">
                  <Camera className="w-3 h-3 text-green-500" />
                  <span className="text-green-600">Camera giao thông ({TRAFFIC_CAMERAS.length})</span>
                </p>
                <div className="space-y-1 text-[10px]">
                  {TRAFFIC_CAMERAS.map((cam) => (
                    <div key={cam.id} className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></div>
                      <span className="truncate">{cam.name}</span>
                    </div>
                  ))}
                </div>
                <p className="text-[9px] text-muted-foreground mt-2 italic">
                  Click vào marker để xem video
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 bg-card rounded-xl border border-border overflow-hidden relative">
          {loading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 animate-spin text-green-600 mx-auto mb-2" />
                <p className="text-muted-foreground">Đang tải bản đồ...</p>
              </div>
            </div>
          ) : mounted ? (
            <MapContainer
              center={mapCenter}
              zoom={mapZoom}
              style={{ height: '100%', width: '100%' }}
              scrollWheelZoom={true}
              ref={mapRef}
            >
              {/* Map Controller for programmatic view changes */}
              <MapController 
                center={mapCenter} 
                zoom={mapZoom} 
                bounds={mapBounds}
              />
              
              {/* Base Map Layer */}
              <TileLayer
                attribution={MAP_LAYERS[activeMapLayer].attribution}
                url={MAP_LAYERS[activeMapLayer].url}
              />
              
              {/* Labels layer for satellite view */}
              {activeMapLayer === 'satellite' && (
                <TileLayer
                  url="https://stamen-tiles-{s}.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://stamen.com">Stamen Design</a>'
                  opacity={0.8}
                />
              )}
              
              {/* Traffic Flow Layer from TomTom */}
              {layerVisibility.traffic && TOMTOM_TRAFFIC_LAYER.url && (
                <TileLayer
                  url={TOMTOM_TRAFFIC_LAYER.url}
                  attribution={TOMTOM_TRAFFIC_LAYER.attribution}
                  opacity={0.7}
                  zIndex={100}
                />
              )}
              
              {/* Hanoi Boundary */}
              {layerVisibility.boundaries && hanoiBoundary && (
                <GeoJSON
                  key="hanoi-boundary"
                  data={hanoiBoundary as any}
                  style={boundaryStyle}
                  onEachFeature={onEachBoundary}
                />
              )}
              
              {/* District Boundaries */}
              {layerVisibility.districts && districtsGeoJSON && (
                <GeoJSON
                  key={geoJsonKey}
                  data={districtsGeoJSON as any}
                  style={getDistrictStyle}
                  onEachFeature={onEachDistrict}
                />
              )}
              
              {/* POI Markers */}
              {layerVisibility.pois && poiMarkers.map((poi) => {
                const config = getPOIConfig(poi.subcategory, poi.category);
                const subcategoryName = poi.subcategory ? (SUBCATEGORY_NAMES[poi.subcategory] || poi.subcategory) : poi.category;
                
                return (
                  <CircleMarker
                    key={poi.id}
                    center={[poi.location.lat, poi.location.lng]}
                    radius={8}
                    pathOptions={{
                      color: '#ffffff',
                      weight: 2,
                      fillColor: config.color,
                      fillOpacity: 0.95,
                    }}
                  >
                    <Popup>
                      <div className="min-w-[220px] max-w-[280px]">
                        {/* Header with emoji and name */}
                        <div className="flex items-start gap-2 mb-2">
                          <span className="text-2xl">{config.emoji}</span>
                          <div className="flex-1">
                            <h4 className="font-bold text-base text-gray-900 leading-tight">{poi.name}</h4>
                            <p className="text-sm text-gray-600 mt-0.5">{subcategoryName}</p>
                          </div>
                        </div>
                        
                        {/* Details */}
                        <div className="space-y-1.5 text-sm border-t border-gray-100 pt-2 mt-2">
                          {poi.address && (
                            <div className="flex items-start gap-2">
                              <span className="text-gray-400 flex-shrink-0">📍</span>
                              <span className="text-gray-700">{poi.address}</span>
                            </div>
                          )}
                          {poi.phone && (
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400">📞</span>
                              <a href={`tel:${poi.phone}`} className="text-blue-600 hover:underline">{poi.phone}</a>
                            </div>
                          )}
                          {poi.website && (
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400">🌐</span>
                              <a 
                                href={poi.website.startsWith('http') ? poi.website : `https://${poi.website}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline truncate max-w-[180px]"
                              >
                                {poi.website.replace(/^https?:\/\//, '').split('/')[0]}
                              </a>
                            </div>
                          )}
                          {poi.opening_hours && (
                            <div className="flex items-start gap-2">
                              <span className="text-gray-400">🕐</span>
                              <span className="text-gray-700">{poi.opening_hours}</span>
                            </div>
                          )}
                        </div>
                        
                        {/* Category badge */}
                        <div className="mt-3 pt-2 border-t border-gray-100">
                          <span 
                            className="inline-block px-2 py-0.5 rounded-full text-xs font-medium text-white"
                            style={{ backgroundColor: config.color }}
                          >
                            {config.name}
                          </span>
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}

              {/* Traffic Camera Markers */}
              {layerVisibility.cameras && TRAFFIC_CAMERAS.map((camera) => (
                <CameraMarkerWithPopup key={camera.id} camera={camera} />
              ))}
            </MapContainer>
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground">Đang khởi tạo bản đồ...</p>
            </div>
          )}

          {/* Map overlay info */}
          {activeBoundaryId && activeDetails && (
            <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-2 rounded-lg text-sm z-[1000]">
              <p className="font-semibold">{activeDetails.boundary.name}</p>
              <p className="text-xs opacity-80">
                {activeDetails.boundary.area_km2.toFixed(2)} km² • {activeDetails.statistics.pois.total} POI
              </p>
            </div>
          )}

          {/* Reset View Button */}
          {(mapBounds || mapZoom !== DEFAULT_ZOOM) && (
            <button
              onClick={resetMapView}
              className="absolute bottom-4 left-4 bg-white dark:bg-gray-800 shadow-lg px-3 py-2 rounded-lg text-sm font-medium z-[1000] hover:bg-green-50 dark:hover:bg-green-950/30 hover:text-green-600 hover:border-green-500 border border-transparent transition-all"
            >
              Xem toàn bộ Hà Nội
            </button>
          )}
        </div>

        {/* Details Panel */}
        {showDetailsPanel && selectedBoundaryIds.length > 0 && (
          <div className="hidden lg:flex lg:flex-col w-96 flex-shrink-0 gap-4 overflow-y-auto">
            {/* Integrated Data Panel - Weather, AQI, Traffic + Infrastructure */}
            <IntegratedDataPanel 
              boundaryId={activeBoundaryId} 
              boundaryName={activeDetails?.boundary.name || ''} 
              boundaryDetails={activeDetails}
            />
          </div>
        )}
      </div>
    </div>
  );
}
