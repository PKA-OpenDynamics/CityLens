"""Add tables for OSM administrative areas and facilities

Revision ID: 3a7f8e9c2d1b
Revises: 2f718b0b0cfe
Create Date: 2025-12-03 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = '3a7f8e9c2d1b'
down_revision = '2f718b0b0cfe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create administrative_areas table
    op.create_table(
        'administrative_areas',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('osm_id', sa.BigInteger(), nullable=False, unique=True, index=True),
        sa.Column('osm_type', sa.String(20), nullable=False),  # 'node', 'way', 'relation'
        sa.Column('admin_level', sa.Integer(), nullable=False, index=True),  # 4, 6, 8
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('name_en', sa.String(255)),
        sa.Column('name_vi', sa.String(255)),
        sa.Column('boundary_type', sa.String(50)),  # 'administrative'
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('administrative_areas.id'), nullable=True, index=True),
        sa.Column('population', sa.Integer()),
        sa.Column('area_km2', sa.Float()),
        sa.Column('tags', JSONB()),  # Store all OSM tags
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326)),  # Can be Point, Polygon, MultiPolygon
        sa.Column('center_point', Geometry(geometry_type='POINT', srid=4326)),  # Always a point for quick queries
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes for spatial queries
    op.create_index('idx_admin_areas_geometry', 'administrative_areas', ['geometry'], postgresql_using='gist')
    op.create_index('idx_admin_areas_center', 'administrative_areas', ['center_point'], postgresql_using='gist')
    
    # Create facilities table
    op.create_table(
        'facilities',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('osm_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('osm_type', sa.String(20), nullable=False),
        sa.Column('category', sa.String(100), nullable=False, index=True),  # 'healthcare', 'education', etc.
        sa.Column('amenity', sa.String(100), nullable=False, index=True),  # 'hospital', 'school', etc.
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_en', sa.String(255)),
        sa.Column('name_vi', sa.String(255)),
        sa.Column('address_street', sa.String(255)),
        sa.Column('address_district', sa.String(100)),
        sa.Column('address_city', sa.String(100)),
        sa.Column('phone', sa.String(50)),
        sa.Column('website', sa.String(255)),
        sa.Column('opening_hours', sa.String(255)),
        sa.Column('admin_area_id', sa.Integer(), sa.ForeignKey('administrative_areas.id'), nullable=True, index=True),
        sa.Column('tags', JSONB()),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Composite unique index to prevent duplicates
    op.create_index('idx_facilities_osm_unique', 'facilities', ['osm_type', 'osm_id', 'amenity'], unique=True)
    
    # Spatial index for location queries
    op.create_index('idx_facilities_location', 'facilities', ['location'], postgresql_using='gist')
    
    # Index for category searches
    op.create_index('idx_facilities_category', 'facilities', ['category', 'amenity'])


def downgrade() -> None:
    op.drop_index('idx_facilities_category', table_name='facilities')
    op.drop_index('idx_facilities_location', table_name='facilities')
    op.drop_index('idx_facilities_osm_unique', table_name='facilities')
    op.drop_table('facilities')
    
    op.drop_index('idx_admin_areas_center', table_name='administrative_areas')
    op.drop_index('idx_admin_areas_geometry', table_name='administrative_areas')
    op.drop_table('administrative_areas')
