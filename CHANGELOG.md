# Changelog

All notable changes to the CityLens project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Issue templates for bug reports and feature requests
- Professional CHANGELOG format

## [0.2.0] - 2025-11-25

### Added

#### Database & Models
- SQLAlchemy declarative base configuration (`backend/app/db/base.py`)
- Geographic models for OSM data (AdministrativeBoundary, Street, Building)
- Facility models for Points of Interest (PublicFacility, TransportFacility)
- Environmental data models for monitoring
- Enhanced user model with additional metadata fields
- Report categories with hierarchical structure

#### Database Migration
- Alembic migration framework setup
- Initial schema migration with all models
- PostGIS extension support for spatial data
- Migration templates and environment configuration

#### Data Collection Scripts
- OSM data download script (`backend/scripts/download_osm.sh`)
  - Downloads Vietnam OSM data from Geofabrik
  - Extracts HCMC region subset
  - Generates GeoJSON for preview
- OSM import script (`backend/scripts/import_osm.py`)
  - Compatible with osmium 4.x API
  - Imports streets, buildings, boundaries, and POIs
  - Handles geometry conversion with WKBFactory
  - Successfully imported 180,000+ streets and 40+ boundaries
- Report categories seeding script
  - 6 main categories (Traffic, Environment, Infrastructure, Security, Public Services, Other)
  - 22 subcategories with Vietnamese translations
- User seeding script with sample data

#### Knowledge Graph
- Neo4j ontology schema (`backend/graphdb/ontology/citylens.ttl`)
- Semantic definitions for urban entities and relationships

#### Documentation
- Project structure documentation
- Database design specifications
- Development roadmap
- Environment setup guide

### Changed
- Updated Python dependencies to support Python 3.14
  - SQLAlchemy 2.0.25 → 2.0.44
  - GeoAlchemy2 0.14.3 → 0.18.1
  - Added osmium 4.2.0 for OSM processing
  - Added shapely for geometry operations
- Updated model exports in `backend/app/models/__init__.py`
- Backend README with improved setup instructions

### Fixed
- Report model: Renamed `metadata` field to `report_metadata` to avoid SQLAlchemy conflict
- Model imports: Removed non-existent `IncidentType` class
- Geographic models: Made `name` fields nullable for unnamed streets/boundaries
- Alembic configuration: Fixed database URL reference in `env.py`
- OSM import script: Rewrote for osmium 4.x compatibility
  - Fixed `Way.get_geometry()` deprecation
  - Implemented WKBFactory and WKTFactory
  - Added proper error handling for geometry conversion

### Security
- Added `.gitignore` rules to exclude:
  - Large OSM data files (*.osm.pbf, *.geojson)
  - Environment configuration files (.env)
  - Database files
  - Sensitive credentials

## [0.1.0] - 2025-11-20

### Added
- Initial project structure
- Basic backend API skeleton with FastAPI
- Web dashboard foundation with React + TypeScript
- Mobile app setup with Flutter
- User authentication models
- Report submission models
- Database schema design
- Docker configuration for development
- CI/CD pipeline setup
- Project documentation

### Infrastructure
- PostgreSQL database setup
- MongoDB for real-time data
- Neo4j knowledge graph foundation
- Redis for caching
- Development environment configuration

---

## Release Categories

### Types of Changes
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security-related changes

### Version Numbering
- **Major** (X.0.0) - Breaking changes
- **Minor** (0.X.0) - New features, backward compatible
- **Patch** (0.0.X) - Bug fixes, backward compatible

---

## Contributing

When adding entries to this changelog:

1. **Unreleased section**: Add changes to `[Unreleased]` first
2. **Version release**: Move changes from `[Unreleased]` to new version section
3. **Format**: Follow the structure above
4. **Links**: Update version comparison links at bottom
5. **Date**: Use ISO 8601 format (YYYY-MM-DD)

Example entry:
```markdown
### Added
- Feature description with relevant file paths
- Component that was added and why
```

---

## Links

[Unreleased]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/PKA-Open-Dynamics/CityLens/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/PKA-Open-Dynamics/CityLens/releases/tag/v0.1.0
