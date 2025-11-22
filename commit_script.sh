#!/bin/bash
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License
# Script to commit project in structured parts

set -e

echo "🚀 Starting structured commit process..."

# Initial setup
git add .gitignore LICENSE CHANGELOG.md CONTRIBUTING.md
git commit -m "chore: add project configuration files" || echo "Already committed"

git add README.md
git commit -m "docs: add comprehensive project documentation" || echo "Already committed"

# Backend - Core
git add backend/requirements.txt backend/Dockerfile backend/.env.example
git commit -m "build(backend): add Python dependencies and Docker config" || echo "Already committed"

git add backend/app/core/config.py
git commit -m "feat(backend): add core configuration management" || echo "Already committed"

git add backend/app/core/security.py
git commit -m "feat(backend): implement JWT authentication and security" || echo "Already committed"

# Backend - Database
git add backend/app/db/postgres.py
git commit -m "feat(backend): add PostgreSQL database connection" || echo "Already committed"

git add backend/app/db/mongodb.py
git commit -m "feat(backend): add MongoDB database connection" || echo "Already committed"

git add backend/app/db/redis.py
git commit -m "feat(backend): add Redis cache connection" || echo "Already committed"

git add backend/app/db/graphdb.py
git commit -m "feat(backend): add GraphDB connection for LOD" || echo "Already committed"

# Backend - Models
git add backend/app/models/user.py
git commit -m "feat(backend): implement User model with roles" || echo "Already committed"

git add backend/app/models/report.py
git commit -m "feat(backend): implement Report model with PostGIS" || echo "Already committed"

git add backend/app/models/incident.py
git commit -m "feat(backend): implement Incident model" || echo "Already committed"

# Backend - Schemas
git add backend/app/schemas/user.py
git commit -m "feat(backend): add User Pydantic schemas" || echo "Already committed"

git add backend/app/schemas/report.py
git commit -m "feat(backend): add Report Pydantic schemas" || echo "Already committed"

git add backend/app/schemas/ngsi_ld.py
git commit -m "feat(backend): implement NGSI-LD schemas" || echo "Already committed"

# Backend - API Endpoints
git add backend/app/api/v1/endpoints/auth.py
git commit -m "feat(backend): implement authentication endpoints" || echo "Already committed"

git add backend/app/api/v1/endpoints/users.py
git commit -m "feat(backend): implement user management endpoints" || echo "Already committed"

git add backend/app/api/v1/endpoints/reports.py
git commit -m "feat(backend): implement report CRUD endpoints" || echo "Already committed"

git add backend/app/api/v1/endpoints/incidents.py
git commit -m "feat(backend): implement incident tracking endpoints" || echo "Already committed"

git add backend/app/api/v1/endpoints/admin.py
git commit -m "feat(backend): implement admin dashboard endpoints" || echo "Already committed"

git add backend/app/api/v1/api.py
git commit -m "feat(backend): add API router configuration" || echo "Already committed"

git add backend/app/main.py
git commit -m "feat(backend): add FastAPI application entry point" || echo "Already committed"

# Web Dashboard - Core
git add web-dashboard/package.json web-dashboard/tsconfig.json web-dashboard/vite.config.ts
git commit -m "build(web): initialize React TypeScript project" || echo "Already committed"

git add web-dashboard/src/theme.ts web-dashboard/src/index.css
git commit -m "style(web): implement minimalist gray-white theme" || echo "Already committed"

git add web-dashboard/src/types/api.ts
git commit -m "feat(web): add TypeScript API interfaces" || echo "Already committed"

# Web Dashboard - Services
git add web-dashboard/src/services/api.ts
git commit -m "feat(web): implement API client with interceptors" || echo "Already committed"

git add web-dashboard/src/services/auth.ts
git commit -m "feat(web): implement authentication service" || echo "Already committed"

git add web-dashboard/src/services/reports.ts
git commit -m "feat(web): implement reports service" || echo "Already committed"

# Web Dashboard - Components
git add web-dashboard/src/components/common/Sidebar.tsx
git commit -m "feat(web): add responsive sidebar navigation" || echo "Already committed"

git add web-dashboard/src/components/common/Header.tsx
git commit -m "feat(web): add header with notifications" || echo "Already committed"

git add web-dashboard/src/components/common/StatCard.tsx
git commit -m "feat(web): add statistics card component" || echo "Already committed"

# Web Dashboard - Pages
git add web-dashboard/src/pages/Login.tsx
git commit -m "feat(web): implement login page" || echo "Already committed"

git add web-dashboard/src/pages/Dashboard.tsx
git commit -m "feat(web): implement dashboard with real-time stats" || echo "Already committed"

git add web-dashboard/src/pages/ReportsPage.tsx
git commit -m "feat(web): implement reports management page" || echo "Already committed"

git add web-dashboard/src/pages/MapPage.tsx web-dashboard/src/pages/AnalyticsPage.tsx
git commit -m "feat(web): add map and analytics pages" || echo "Already committed"

git add web-dashboard/src/App.tsx web-dashboard/src/main.tsx
git commit -m "feat(web): configure app routing and layout" || echo "Already committed"

git add web-dashboard/Dockerfile web-dashboard/nginx.conf
git commit -m "build(web): add Docker and Nginx configuration" || echo "Already committed"

# Mobile App
git add mobile-app/pubspec.yaml mobile-app/analysis_options.yaml
git commit -m "build(mobile): initialize Flutter project" || echo "Already committed"

git add mobile-app/lib/core/
git commit -m "feat(mobile): add core constants and theme" || echo "Already committed"

git add mobile-app/lib/features/auth/
git commit -m "feat(mobile): implement authentication feature" || echo "Already committed"

git add mobile-app/lib/features/map/
git commit -m "feat(mobile): implement map feature" || echo "Already committed"

git add mobile-app/lib/main.dart
git commit -m "feat(mobile): add app entry point" || echo "Already committed"

git add mobile-app/ios/ mobile-app/android/
git commit -m "build(mobile): configure iOS and Android platforms" || echo "Already committed"

# Infrastructure
git add docker-compose.yml docker-compose.prod.yml
git commit -m "build: add Docker Compose orchestration" || echo "Already committed"

# CI/CD
git add .github/workflows/
git commit -m "ci: add GitHub Actions workflows" || echo "Already committed"

# Final commit for any remaining files
git add .
git commit -m "chore: finalize project structure" || echo "Already committed"

echo "✅ Completed! Total commits created."
echo "📊 Checking commit count..."
git log --oneline | wc -l
