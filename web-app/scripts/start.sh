#!/bin/bash
# Start script for CityLens Web App

set -e

echo "🚀 Starting CityLens Web App..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update with your configuration."
    else
        echo "EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" > .env
        echo "✅ Created default .env file."
    fi
fi

# Start Expo
echo "🌐 Starting Expo development server..."
npx expo start


