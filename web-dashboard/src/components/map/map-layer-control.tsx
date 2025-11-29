// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState } from 'react';
import { Layers, MapPin, Navigation2, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MapLayerControlProps {
  onLayerChange?: (layers: string[]) => void;
}

export default function MapLayerControl({ onLayerChange }: MapLayerControlProps) {
  const [activeLayers, setActiveLayers] = useState<string[]>(['poi']);

  const layers = [
    { id: 'poi', name: 'Điểm quan tâm', icon: MapPin, color: 'text-blue-500' },
    { id: 'traffic', name: 'Giao thông', icon: Navigation2, color: 'text-red-500' },
    { id: 'facilities', name: 'Cơ sở vật chất', icon: Layers, color: 'text-green-500' },
    { id: 'incidents', name: 'Sự cố', icon: Zap, color: 'text-yellow-500' },
  ];

  const toggleLayer = (layerId: string) => {
    const newLayers = activeLayers.includes(layerId)
      ? activeLayers.filter(id => id !== layerId)
      : [...activeLayers, layerId];
    
    setActiveLayers(newLayers);
    onLayerChange?.(newLayers);
  };

  return (
    <div className="absolute top-20 right-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 min-w-[200px]">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
        <Layers className="h-4 w-4" />
        Lớp dữ liệu
      </h3>
      <div className="space-y-2">
        {layers.map((layer) => {
          const Icon = layer.icon;
          const isActive = activeLayers.includes(layer.id);
          
          return (
            <button
              key={layer.id}
              onClick={() => toggleLayer(layer.id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all',
                isActive
                  ? 'bg-accent/10 text-accent border border-accent/20'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              )}
            >
              <Icon className={cn('h-4 w-4', isActive ? 'text-accent' : layer.color)} />
              <span className="flex-1 text-left">{layer.name}</span>
              <div className={cn(
                'w-3 h-3 rounded-full border-2 transition-all',
                isActive 
                  ? 'bg-accent border-accent' 
                  : 'border-gray-300 dark:border-gray-600'
              )} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
