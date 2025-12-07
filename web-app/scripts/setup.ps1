# Setup script for CityLens Web App (PowerShell)

Write-Host "Setting up CityLens Web App..." -ForegroundColor Green

# Check Node.js version
$nodeVersion = (node -v) -replace 'v', ''
$majorVersion = [int]($nodeVersion -split '\.')[0]
if ($majorVersion -lt 18) {
    Write-Host "Error: Node.js 18.x or higher is required. Current version: $(node -v)" -ForegroundColor Red
    exit 1
}

Write-Host "Node.js version: $(node -v)" -ForegroundColor Green

# Check npm version
Write-Host "npm version: $(npm -v)" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    } else {
        "EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" | Out-File -FilePath ".env" -Encoding utf8
    }
    Write-Host "Created .env file" -ForegroundColor Green
}

Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the app, run:" -ForegroundColor Cyan
Write-Host "  npm start" -ForegroundColor White
Write-Host "  or" -ForegroundColor White
Write-Host "  .\scripts\start.ps1" -ForegroundColor White
