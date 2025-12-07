# Build script for CityLens Web App (PowerShell)

Write-Host "Building CityLens Web App..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Build for web
Write-Host "Building for web..." -ForegroundColor Yellow
npx expo export:web

Write-Host "Build completed! Output in 'web-build/' directory" -ForegroundColor Green
