#!/bin/bash

# CityLens Backend - One-Command Docker Setup
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

set -e

echo "================================================"
echo "CityLens Backend - Docker Quick Setup"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "Step 1: Setting up environment..."

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "SUCCESS: .env file created"
    echo ""
    echo "NOTE: Edit .env to add your API keys if needed:"
    echo "  - OPENWEATHER_API_KEY"
    echo "  - TOMTOM_API_KEY"
    echo "  - AQICN_API_KEY"
    echo ""
else
    echo "INFO: .env file already exists"
fi

echo ""
echo "Step 2: Building Docker image..."
docker build -t citylens-backend .

echo ""
echo "Step 3: Starting containers..."

# Stop existing containers if any
docker-compose down 2>/dev/null || true

# Start only required services for backend
docker-compose up -d postgres redis

echo ""
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Wait for postgres to be healthy
until docker exec citylens-postgres-prod pg_isready -U citylens 2>/dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo ""
echo "Step 4: Starting Backend API..."
docker-compose up -d backend

echo ""
echo "================================================"
echo "SUCCESS! CityLens Backend is ready!"
echo "================================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f backend"
echo ""
echo "To import database (487K+ OSM entities):"
echo "  See DATABASE_IMPORT.md for instructions"
echo ""
echo "To stop:"
echo "  docker-compose down"
echo ""
