// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Search, X, MapPin, ChevronDown, Check } from 'lucide-react';
import { geographicApi, type BoundarySimpleItem } from '@/lib/api';
import { cn } from '@/lib/utils';

interface BoundarySelectorProps {
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
  maxSelection?: number;
  className?: string;
}

export function BoundarySelector({
  selectedIds,
  onSelectionChange,
  maxSelection = 10,
  className,
}: BoundarySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [boundaries, setBoundaries] = useState<BoundarySimpleItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch boundaries list
  useEffect(() => {
    const fetchBoundaries = async () => {
      try {
        const response = await geographicApi.getBoundariesListSimple(6);
        setBoundaries(response.items);
      } catch (error) {
        console.error('Error fetching boundaries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBoundaries();
  }, []);

  // Filter boundaries by search
  const filteredBoundaries = useMemo(() => {
    if (!searchQuery.trim()) return boundaries;
    
    const query = searchQuery.toLowerCase();
    return boundaries.filter(
      (b) =>
        b.name.toLowerCase().includes(query) ||
        (b.name_en && b.name_en.toLowerCase().includes(query))
    );
  }, [boundaries, searchQuery]);

  // Group by type (Phường / Xã)
  const groupedBoundaries = useMemo(() => {
    const phuong = filteredBoundaries.filter((b) => b.name.startsWith('Phường'));
    const xa = filteredBoundaries.filter((b) => b.name.startsWith('Xã'));
    return { phuong, xa };
  }, [filteredBoundaries]);

  // Selected items
  const selectedItems = useMemo(
    () => boundaries.filter((b) => selectedIds.includes(b.id)),
    [boundaries, selectedIds]
  );

  const toggleSelection = useCallback(
    (id: number) => {
      if (selectedIds.includes(id)) {
        onSelectionChange(selectedIds.filter((i) => i !== id));
      } else if (selectedIds.length < maxSelection) {
        onSelectionChange([...selectedIds, id]);
      }
    },
    [selectedIds, onSelectionChange, maxSelection]
  );

  const clearSelection = useCallback(() => {
    onSelectionChange([]);
  }, [onSelectionChange]);

  const selectAll = useCallback(
    (type: 'phuong' | 'xa') => {
      const items = type === 'phuong' ? groupedBoundaries.phuong : groupedBoundaries.xa;
      const idsToAdd = items.slice(0, maxSelection - selectedIds.length).map((b) => b.id);
      onSelectionChange([...new Set([...selectedIds, ...idsToAdd])]);
    },
    [groupedBoundaries, selectedIds, maxSelection, onSelectionChange]
  );

  return (
    <div className={cn('relative', className)}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full flex items-center justify-between gap-2 px-4 py-2.5 rounded-lg',
          'bg-card border border-border hover:bg-muted transition-colors text-left'
        )}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <MapPin className="w-4 h-4 text-muted-foreground flex-shrink-0" />
          {selectedItems.length > 0 ? (
            <span className="truncate text-foreground">
              {selectedItems.length === 1
                ? selectedItems[0].name
                : `${selectedItems.length} đơn vị đã chọn`}
            </span>
          ) : (
            <span className="text-muted-foreground">Chọn phường/xã...</span>
          )}
        </div>
        <ChevronDown
          className={cn('w-4 h-4 text-muted-foreground transition-transform', isOpen && 'rotate-180')}
        />
      </button>

      {/* Selected Tags */}
      {selectedItems.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {selectedItems.map((item) => (
            <span
              key={item.id}
              className="inline-flex items-center gap-1 px-2 py-1 bg-accent/10 text-accent rounded-md text-xs"
            >
              {item.name}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleSelection(item.id);
                }}
                className="hover:text-accent-foreground"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {selectedItems.length > 1 && (
            <button
              onClick={clearSelection}
              className="px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
            >
              Xóa tất cả
            </button>
          )}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-[9998]" onClick={() => setIsOpen(false)} />

          {/* Dropdown Content */}
          <div className="absolute top-full left-0 right-0 mt-1 z-[9999] bg-card border border-border rounded-lg shadow-xl max-h-[60vh] overflow-hidden">
            {/* Search */}
            <div className="p-2 border-b border-border">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Tìm kiếm phường/xã..."
                  className="w-full pl-9 pr-4 py-2 bg-muted rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                  autoFocus
                />
              </div>
            </div>

            {/* Stats */}
            <div className="px-3 py-2 text-xs text-muted-foreground border-b border-border flex justify-between">
              <span>
                {filteredBoundaries.length} / {boundaries.length} đơn vị
              </span>
              <span>Đã chọn: {selectedIds.length} / {maxSelection}</span>
            </div>

            {/* List */}
            <div className="overflow-y-auto" style={{ maxHeight: 'calc(60vh - 100px)' }}>
              {loading ? (
                <div className="p-4 text-center text-muted-foreground">Đang tải...</div>
              ) : filteredBoundaries.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">Không tìm thấy</div>
              ) : (
                <>
                  {/* Phường Section */}
                  {groupedBoundaries.phuong.length > 0 && (
                    <div>
                      <div className="sticky top-0 bg-muted px-3 py-1.5 flex justify-between items-center">
                        <span className="text-xs font-medium text-muted-foreground">
                          Phường ({groupedBoundaries.phuong.length})
                        </span>
                        <button
                          onClick={() => selectAll('phuong')}
                          className="text-xs text-accent hover:underline"
                        >
                          Chọn tất cả
                        </button>
                      </div>
                      {groupedBoundaries.phuong.map((boundary) => (
                        <BoundaryItem
                          key={boundary.id}
                          boundary={boundary}
                          isSelected={selectedIds.includes(boundary.id)}
                          onToggle={() => toggleSelection(boundary.id)}
                          disabled={
                            !selectedIds.includes(boundary.id) && selectedIds.length >= maxSelection
                          }
                        />
                      ))}
                    </div>
                  )}

                  {/* Xã Section */}
                  {groupedBoundaries.xa.length > 0 && (
                    <div>
                      <div className="sticky top-0 bg-muted px-3 py-1.5 flex justify-between items-center">
                        <span className="text-xs font-medium text-muted-foreground">
                          Xã ({groupedBoundaries.xa.length})
                        </span>
                        <button
                          onClick={() => selectAll('xa')}
                          className="text-xs text-accent hover:underline"
                        >
                          Chọn tất cả
                        </button>
                      </div>
                      {groupedBoundaries.xa.map((boundary) => (
                        <BoundaryItem
                          key={boundary.id}
                          boundary={boundary}
                          isSelected={selectedIds.includes(boundary.id)}
                          onToggle={() => toggleSelection(boundary.id)}
                          disabled={
                            !selectedIds.includes(boundary.id) && selectedIds.length >= maxSelection
                          }
                        />
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Individual boundary item
function BoundaryItem({
  boundary,
  isSelected,
  onToggle,
  disabled,
}: {
  boundary: BoundarySimpleItem;
  isSelected: boolean;
  onToggle: () => void;
  disabled: boolean;
}) {
  return (
    <button
      onClick={onToggle}
      disabled={disabled}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-muted transition-colors',
        isSelected && 'bg-accent/10',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <div
        className={cn(
          'w-4 h-4 rounded border flex items-center justify-center flex-shrink-0',
          isSelected ? 'bg-accent border-accent' : 'border-border'
        )}
      >
        {isSelected && <Check className="w-3 h-3 text-white" />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{boundary.name}</p>
        {boundary.name_en && (
          <p className="text-xs text-muted-foreground truncate">{boundary.name_en}</p>
        )}
      </div>
      <span className="text-xs text-muted-foreground flex-shrink-0">
        {boundary.area_km2.toFixed(1)} km²
      </span>
    </button>
  );
}

export default BoundarySelector;
