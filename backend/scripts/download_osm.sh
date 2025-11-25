#!/bin/bash
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

# Download và extract OSM data cho TP. Hồ Chí Minh
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

# Extract TP.HCM (Ho Chi Minh City)
# Bounding box: minlon, minlat, maxlon, maxlat
# HCM City: 106.4, 10.5, 107.0, 11.0
echo "Extracting Ho Chi Minh City data..."
osmium extract \
    --bbox 106.4,10.5,107.0,11.0 \
    data/osm/vietnam-latest.osm.pbf \
    -o data/osm/hcmc.osm.pbf \
    --overwrite

echo "✓ Extracted hcmc.osm.pbf (~50MB)"

# Convert to GeoJSON (optional - for inspection)
if command -v osmium &> /dev/null; then
    echo "Converting to GeoJSON..."
    osmium export data/osm/hcmc.osm.pbf \
        -o data/osm/hcmc.geojson \
        --overwrite
    echo "✓ Created hcmc.geojson"
fi

echo ""
echo "✅ OSM data download completed!"
echo ""
echo "Files created:"
echo "  - data/osm/vietnam-latest.osm.pbf (~500MB)"
echo "  - data/osm/hcmc.osm.pbf (~50MB)"
echo "  - data/osm/hcmc.geojson"
echo ""
echo "Next step: Run import script"
echo "  python scripts/import_osm.py"
