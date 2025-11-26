// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, CircleMarker, Tooltip, Circle, Polygon } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import './MapStyles.css';
import 'leaflet.markercluster';
import { Box, Paper, IconButton, Chip, ToggleButton, ToggleButtonGroup, Tooltip as MuiTooltip } from '@mui/material';
import { 
  MyLocation, 
  Layers, 
  Add, 
  Remove, 
  Terrain,
  Opacity,
  FilterList,
  LocationOn,
  Whatshot
} from '@mui/icons-material';

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface MapMarker {
  id: string;
  type: 'report' | 'sensor' | 'facility';
  coordinates: [number, number];
  title: string;
  description?: string;
  severity?: 'low' | 'medium' | 'high';
}

interface CityMapProps {
  center?: [number, number];
  zoom?: number;
  markers?: MapMarker[];
  onMarkerClick?: (marker: MapMarker) => void;
}

// Enhanced custom icons with SVG
const createCustomIcon = (type: string, severity?: string) => {
  let color = '#2196f3';
  let icon = '●';
  
  if (type === 'report') {
    color = severity === 'high' ? '#f44336' : 
            severity === 'medium' ? '#ff9800' : '#4caf50';
    icon = '⚠';
  } else if (type === 'facility') {
    color = '#9c27b0';
    icon = '■';
  } else if (type === 'sensor') {
    icon = '◆';
  }

  return L.divIcon({
    className: 'custom-marker-enhanced',
    html: `
      <div style="
        position: relative;
        width: 40px;
        height: 40px;
      ">
        <!-- Pulse animation -->
        <div style="
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 40px;
          height: 40px;
          background-color: ${color};
          border-radius: 50%;
          opacity: 0.4;
          animation: pulse 2s infinite;
        "></div>
        
        <!-- Main marker -->
        <div style="
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%);
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          color: white;
          font-weight: bold;
        ">
          ${icon}
        </div>
      </div>
      <style>
        @keyframes pulse {
          0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.6; }
          50% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
          100% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.6; }
        }
      </style>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  });
};

// Custom cluster icon
const createClusterCustomIcon = (cluster: any) => {
  const count = cluster.getChildCount();
  let size = 40;
  let color = '#2196f3';
  
  if (count > 100) {
    size = 60;
    color = '#f44336';
  } else if (count > 50) {
    size = 50;
    color = '#ff9800';
  }

  return L.divIcon({
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background: linear-gradient(135deg, ${color} 0%, ${color}cc 100%);
        border: 4px solid white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${size > 50 ? '18px' : '14px'};
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        animation: clusterPulse 2s infinite;
      ">
        ${count}
      </div>
      <style>
        @keyframes clusterPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
      </style>
    `,
    className: 'marker-cluster-custom',
    iconSize: L.point(size, size),
  });
};

// Hanoi District boundaries (simplified)
const HANOI_DISTRICTS = [
  { name: 'Hoàn Kiếm', center: [21.0285, 105.8542], radius: 2000, population: 133000 },
  { name: 'Ba Đình', center: [21.0333, 105.8197], radius: 2200, population: 221000 },
  { name: 'Đống Đa', center: [21.0182, 105.8270], radius: 2400, population: 344000 },
  { name: 'Hai Bà Trưng', center: [21.0067, 105.8521], radius: 2300, population: 302000 },
  { name: 'Thanh Xuân', center: [20.9952, 105.8079], radius: 2500, population: 295000 },
  { name: 'Cầu Giấy', center: [21.0333, 105.7940], radius: 2600, population: 302000 },
  { name: 'Long Biên', center: [21.0533, 105.8344], radius: 2800, population: 289000 },
  { name: 'Tây Hồ', center: [21.0783, 105.8190], radius: 3000, population: 135000 },
];

// Map layer styles
const MAP_LAYERS = [
  {
    name: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors'
  },
  {
    name: 'CartoDB Light',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; OpenStreetMap &copy; CARTO'
  },
  {
    name: 'CartoDB Dark',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; OpenStreetMap &copy; CARTO'
  },
  {
    name: 'Esri World',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri'
  },
];

// Marker clustering component
function MarkerClustering({ markers, onMarkerClick, clusteringEnabled }: any) {
  const map = useMap();

  useEffect(() => {
    if (!clusteringEnabled) return;

    // Use L.markerClusterGroup instead of MarkerClusterGroup
    const markerClusterGroup = (L as any).markerClusterGroup({
      iconCreateFunction: createClusterCustomIcon,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 80,
      disableClusteringAtZoom: 16,
    });

    markers.forEach((marker: MapMarker) => {
      const leafletMarker = L.marker(marker.coordinates, {
        icon: createCustomIcon(marker.type, marker.severity),
      });

      leafletMarker.bindPopup(`
        <div style="padding: 8px; min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">
            ${marker.title}
          </h4>
          ${marker.description ? `<p style="margin: 0; font-size: 12px; color: #666;">${marker.description}</p>` : ''}
        </div>
      `);

      leafletMarker.on('click', () => {
        if (onMarkerClick) onMarkerClick(marker);
      });

      markerClusterGroup.addLayer(leafletMarker);
    });

    map.addLayer(markerClusterGroup);

    return () => {
      map.removeLayer(markerClusterGroup);
    };
  }, [map, markers, onMarkerClick, clusteringEnabled]);

  return null;
}

// Map controls component
function MapControls({ 
  center, 
  zoom, 
  onLayerChange, 
  currentLayer,
  onViewChange,
  currentView 
}: any) {
  const map = useMap();

  const handleResetView = () => {
    map.setView(center, zoom);
  };

  const handleZoomIn = () => {
    map.zoomIn();
  };

  const handleZoomOut = () => {
    map.zoomOut();
  };

  const handleLocate = () => {
    map.locate({ setView: true, maxZoom: 16 });
  };

  return (
    <>
      {/* Main controls */}
      <Paper
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          gap: 0.5,
          p: 0.5,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <MuiTooltip title="Về vị trí ban đầu" placement="right">
          <IconButton size="small" onClick={handleResetView}>
            <Layers fontSize="small" />
          </IconButton>
        </MuiTooltip>
        
        <MuiTooltip title="Vị trí của tôi" placement="right">
          <IconButton size="small" onClick={handleLocate}>
            <MyLocation fontSize="small" />
          </IconButton>
        </MuiTooltip>
        
        <MuiTooltip title="Phóng to" placement="right">
          <IconButton size="small" onClick={handleZoomIn}>
            <Add fontSize="small" />
          </IconButton>
        </MuiTooltip>
        
        <MuiTooltip title="Thu nhỏ" placement="right">
          <IconButton size="small" onClick={handleZoomOut}>
            <Remove fontSize="small" />
          </IconButton>
        </MuiTooltip>
      </Paper>

      {/* Layer switcher */}
      <Paper
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 1000,
          p: 1,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <ToggleButtonGroup
          value={currentLayer}
          exclusive
          onChange={onLayerChange}
          size="small"
          orientation="vertical"
        >
          {MAP_LAYERS.map((layer, idx) => (
            <ToggleButton key={idx} value={idx}>
              {layer.name}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Paper>

      {/* View mode switcher */}
      <Paper
        sx={{
          position: 'absolute',
          top: 200,
          right: 16,
          zIndex: 1000,
          p: 1,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <ToggleButtonGroup
          value={currentView}
          exclusive
          onChange={onViewChange}
          size="small"
          orientation="vertical"
        >
          <MuiTooltip title="Markers" placement="left">
            <ToggleButton value="markers">
              <LocationOn fontSize="small" />
            </ToggleButton>
          </MuiTooltip>
          <MuiTooltip title="Heatmap" placement="left">
            <ToggleButton value="heatmap">
              <Whatshot fontSize="small" />
            </ToggleButton>
          </MuiTooltip>
          <MuiTooltip title="Density" placement="left">
            <ToggleButton value="density">
              <Opacity fontSize="small" />
            </ToggleButton>
          </MuiTooltip>
        </ToggleButtonGroup>
      </Paper>
    </>
  );
}

// Zoom indicator
function ZoomIndicator() {
  const map = useMap();
  const [currentZoom, setCurrentZoom] = useState(map.getZoom());

  useEffect(() => {
    const onZoom = () => {
      setCurrentZoom(Math.round(map.getZoom()));
    };
    map.on('zoom', onZoom);
    return () => {
      map.off('zoom', onZoom);
    };
  }, [map]);

  return (
    <Chip
      label={`Zoom: ${currentZoom}x`}
      size="small"
      sx={{
        position: 'absolute',
        bottom: 24,
        right: 16,
        zIndex: 1000,
        bgcolor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(8px)',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        fontWeight: 600,
      }}
    />
  );
}

export default function CityMap({
  center = [21.0285, 105.8542],
  zoom = 12,
  markers = [],
  onMarkerClick,
}: CityMapProps) {
  const [currentLayer, setCurrentLayer] = useState(0);
  const [currentView, setCurrentView] = useState('markers');
  const [clusteringEnabled, setClusteringEnabled] = useState(true);

  const handleLayerChange = (_: any, newLayer: number) => {
    if (newLayer !== null) {
      setCurrentLayer(newLayer);
    }
  };

  const handleViewChange = (_: any, newView: string) => {
    if (newView !== null) {
      setCurrentView(newView);
      setClusteringEnabled(newView === 'markers');
    }
  };

  // Group markers by severity for heatmap
  const heatmapData = useMemo(() => {
    return markers
      .filter(m => m.type === 'report')
      .map(m => ({
        lat: m.coordinates[0],
        lng: m.coordinates[1],
        intensity: m.severity === 'high' ? 1 : m.severity === 'medium' ? 0.6 : 0.3
      }));
  }, [markers]);

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%', borderRadius: '8px' }}
        zoomControl={false}
        preferCanvas={true}
      >
        <TileLayer
          attribution={MAP_LAYERS[currentLayer].attribution}
          url={MAP_LAYERS[currentLayer].url}
          maxZoom={19}
        />

        {/* District boundaries */}
        {currentView !== 'heatmap' && HANOI_DISTRICTS.map((district, idx) => (
          <Circle
            key={idx}
            center={district.center}
            radius={district.radius}
            pathOptions={{
              color: '#2196f3',
              fillColor: '#2196f3',
              fillOpacity: 0.05,
              weight: 2,
              opacity: 0.3,
            }}
          >
            <Tooltip permanent direction="center" className="district-label">
              <span style={{ 
                fontSize: '11px', 
                fontWeight: 600,
                color: '#2196f3',
                textShadow: '1px 1px 2px white',
              }}>
                {district.name}
              </span>
            </Tooltip>
          </Circle>
        ))}

        {/* Markers view */}
        {currentView === 'markers' && clusteringEnabled && (
          <MarkerClustering
            markers={markers}
            onMarkerClick={onMarkerClick}
            clusteringEnabled={clusteringEnabled}
          />
        )}

        {currentView === 'markers' && !clusteringEnabled && markers.map((marker) => (
          <Marker
            key={marker.id}
            position={marker.coordinates}
            icon={createCustomIcon(marker.type, marker.severity)}
            eventHandlers={{
              click: () => onMarkerClick?.(marker),
            }}
          >
            <Popup>
              <Box sx={{ p: 1, minWidth: 200 }}>
                <Box sx={{ fontWeight: 600, fontSize: 14, mb: 1 }}>
                  {marker.title}
                </Box>
                {marker.description && (
                  <Box sx={{ fontSize: 12, color: 'text.secondary' }}>
                    {marker.description}
                  </Box>
                )}
              </Box>
            </Popup>
          </Marker>
        ))}

        {/* Density view - Circle markers */}
        {currentView === 'density' && markers.map((marker) => {
          const radius = marker.severity === 'high' ? 300 : 
                        marker.severity === 'medium' ? 200 : 100;
          const color = marker.type === 'report' 
            ? (marker.severity === 'high' ? '#f44336' : 
               marker.severity === 'medium' ? '#ff9800' : '#4caf50')
            : marker.type === 'sensor' ? '#2196f3' : '#9c27b0';

          return (
            <Circle
              key={marker.id}
              center={marker.coordinates}
              radius={radius}
              pathOptions={{
                color: color,
                fillColor: color,
                fillOpacity: 0.2,
                weight: 2,
                opacity: 0.6,
              }}
            >
              <Popup>
                <Box sx={{ p: 1 }}>
                  <Box sx={{ fontWeight: 600, fontSize: 14 }}>{marker.title}</Box>
                </Box>
              </Popup>
            </Circle>
          );
        })}

        <MapControls 
          center={center} 
          zoom={zoom}
          onLayerChange={handleLayerChange}
          currentLayer={currentLayer}
          onViewChange={handleViewChange}
          currentView={currentView}
        />
        <ZoomIndicator />
      </MapContainer>

      {/* Enhanced Legend */}
      <Paper
        sx={{
          position: 'absolute',
          bottom: 16,
          left: 16,
          zIndex: 1000,
          p: 2,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          minWidth: 220,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
          <FilterList fontSize="small" color="primary" />
          <Box sx={{ fontWeight: 700, fontSize: 14, color: 'primary.main' }}>
            Chú thích
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: '#f44336',
                border: '3px solid white',
                boxShadow: '0 2px 8px rgba(244,67,54,0.4)',
              }}
            />
            <Box sx={{ fontSize: 13, fontWeight: 500 }}>Báo cáo khẩn cấp</Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: '#ff9800',
                border: '3px solid white',
                boxShadow: '0 2px 8px rgba(255,152,0,0.4)',
              }}
            />
            <Box sx={{ fontSize: 13, fontWeight: 500 }}>Báo cáo trung bình</Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: '#2196f3',
                border: '3px solid white',
                boxShadow: '0 2px 8px rgba(33,150,243,0.4)',
              }}
            />
            <Box sx={{ fontSize: 13, fontWeight: 500 }}>Cảm biến IoT</Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: '#9c27b0',
                border: '3px solid white',
                boxShadow: '0 2px 8px rgba(156,39,176,0.4)',
              }}
            />
            <Box sx={{ fontSize: 13, fontWeight: 500 }}>Cơ sở hạ tầng</Box>
          </Box>
        </Box>

        {currentView === 'markers' && (
          <Box sx={{ 
            mt: 2, 
            pt: 2, 
            borderTop: '1px solid rgba(0,0,0,0.1)',
            fontSize: 11,
            color: 'text.secondary',
            textAlign: 'center'
          }}>
            💡 Click markers để xem chi tiết
          </Box>
        )}
      </Paper>
    </Box>
  );
}
