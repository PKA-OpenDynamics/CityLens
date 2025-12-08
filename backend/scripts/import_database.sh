#!/bin/bash

# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

# Script to import SQL dump into PostgreSQL database
# Can be used with local or Docker PostgreSQL instance

set -e

echo "🚀 CityLens Database Import Script"
echo "===================================="

# Check if dump file is provided
if [ -z "$1" ]; then
    DUMP_FILE="./data/seeds/citylens_latest.sql"
    echo "ℹ️  No dump file specified, using latest: $DUMP_FILE"
else
    DUMP_FILE="$1"
    echo "ℹ️  Using specified dump file: $DUMP_FILE"
fi

# Check if dump file exists
if [ ! -f "$DUMP_FILE" ]; then
    echo "❌ Error: Dump file not found: $DUMP_FILE"
    echo ""
    echo "Available dump files in ./data/seeds/:"
    ls -lh ./data/seeds/*.sql 2>/dev/null || echo "  (none found)"
    echo ""
    echo "Usage:"
    echo "  $0 [dump_file.sql]"
    echo ""
    echo "Example:"
    echo "  $0 ./data/seeds/citylens_dump_20250101_120000.sql"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found, using default values"
    POSTGRES_SERVER=${POSTGRES_SERVER:-localhost}
    POSTGRES_PORT=${POSTGRES_PORT:-5432}
    POSTGRES_USER=${POSTGRES_USER:-citylens}
    POSTGRES_DB=${POSTGRES_DB:-citylens}
fi

echo ""
echo "📊 Target Database:"
echo "  - Server: $POSTGRES_SERVER:$POSTGRES_PORT"
echo "  - Database: $POSTGRES_DB"
echo "  - User: $POSTGRES_USER"
echo ""

# Get dump file size
FILE_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
echo "📦 Dump file size: $FILE_SIZE"
echo ""

# Warning prompt
read -p "⚠️  This will DROP existing database and recreate it. Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Import cancelled."
    exit 0
fi

echo ""
echo "💾 Importing database from: $DUMP_FILE"
echo "This may take a few minutes for 487K+ entities..."
echo ""

# Import database
PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_SERVER" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d postgres \
    -v ON_ERROR_STOP=1 \
    < "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database imported successfully!"
    echo ""
    
    # Verify import
    echo "🔍 Verifying import..."
    ENTITY_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql \
        -h "$POSTGRES_SERVER" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        -t -c "SELECT COUNT(*) FROM osm_entities;" 2>/dev/null || echo "0")
    
    echo "📊 Total OSM entities: $(echo $ENTITY_COUNT | xargs)"
    echo ""
    
    echo "🎉 Import complete! Your database is ready to use."
    echo ""
    echo "Next steps:"
    echo "  1. Start the backend: uvicorn app.main:app --reload"
    echo "  2. Access API docs: http://localhost:8000/docs"
    echo "  3. Check health: curl http://localhost:8000/health"
    
else
    echo ""
    echo "❌ Error: Database import failed!"
    exit 1
fi
