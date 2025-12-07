# Start script for CityLens Web App (PowerShell)

Write-Host "Starting CityLens Web App..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file. Please update with your configuration." -ForegroundColor Green
    } else {
        "EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "Created default .env file." -ForegroundColor Green
    }
}

# Start Expo
Write-Host "Starting Expo development server..." -ForegroundColor Yellow
npx expo start
