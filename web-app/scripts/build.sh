#!/bin/bash
# Build script for CityLens Web App

set -e

echo "🚀 Building CityLens Web App..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build for web
echo "🌐 Building for web..."
npx expo export:web

echo "✅ Build completed! Output in 'web-build/' directory"


