#!/bin/bash
# Setup script for CityLens Web App

set -e

echo "🔧 Setting up CityLens Web App..."

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js 18.x or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check npm version
echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
EOF
    fi
    echo "✅ Created .env file"
fi

echo "✅ Setup completed!"
echo ""
echo "To start the app, run:"
echo "  npm start"
echo "  or"
echo "  ./scripts/start.sh"


