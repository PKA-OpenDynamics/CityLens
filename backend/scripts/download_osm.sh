#!/bin/bash
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

# Download và extract OSM data cho Hà Nội
# Chạy: bash scripts/download_osm.sh

set -e

echo "📦 Downloading OSM data for Vietnam..."

# Tạo thư mục data nếu chưa có
mkdir -p data/osm

# Download Vietnam OSM data từ Geofabrik
if [ ! -f data/osm/vietnam-latest.osm.pbf ]; then
    echo "Downloading vietnam-latest.osm.pbf (~500MB)..."
    wget -O data/osm/vietnam-latest.osm.pbf \
        https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
    echo "✓ Downloaded vietnam-latest.osm.pbf"
else
    echo "- vietnam-latest.osm.pbf already exists"
fi

# Check if osmium-tool is installed
if ! command -v osmium &> /dev/null; then
    echo "⚠️  osmium-tool is not installed"
    echo "Install on macOS: brew install osmium-tool"
    echo "Install on Ubuntu: apt-get install osmium-tool"
    exit 1
fi

# Extract Hà Nội
# Bounding box: minlon, minlat, maxlon, maxlat
# Hanoi: 105.6, 20.8, 106.0, 21.3
echo "Extracting Hanoi data..."
osmium extract \
    --bbox 105.6,20.8,106.0,21.3 \
    data/osm/vietnam-latest.osm.pbf \
    -o data/osm/hanoi.osm.pbf \
    --overwrite

echo "✓ Extracted hanoi.osm.pbf (~50MB)"

# Convert to GeoJSON (optional - for inspection)
if command -v osmium &> /dev/null; then
    echo "Converting to GeoJSON..."
    osmium export data/osm/hanoi.osm.pbf \
        -o data/osm/hanoi.geojson \
        --overwrite
    echo "✓ Created hanoi.geojson"
fi

echo ""
echo "✅ OSM data download completed!"
echo ""
echo "Files created:"
echo "  - data/osm/vietnam-latest.osm.pbf (~500MB)"
echo "  - data/osm/hanoi.osm.pbf (~50MB)"
echo "  - data/osm/hanoi.geojson"
echo ""
echo "Next step: Run import script"
echo "  python scripts/import_osm.py"
