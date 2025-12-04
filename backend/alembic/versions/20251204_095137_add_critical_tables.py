# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""add_critical_tables

Revision ID: 4c8f9e3d1a2b
Revises: 68e1fcc220f6
Create Date: 2025-12-04 09:51:37

Adds critical tables for Phase 1:
- user_device_tokens: For push notifications
- media_files: File storage management
- report_media: Report-media relationship
- sensor_observations: SOSA/SSN observations
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '4c8f9e3d1a2b'
down_revision = '68e1fcc220f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # 1. USER DEVICE TOKENS - For push notifications (FCM/APNs)
    # =========================================================================
    op.create_table(
        'user_device_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_type', sa.String(length=20), nullable=False, comment='ios, android, web'),
        sa.Column('token', sa.Text(), nullable=False, comment='FCM/APNs token'),
        sa.Column('device_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Device metadata: model, os_version, app_version'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_device_token')
    )
    op.create_index('idx_device_tokens_user_id', 'user_device_tokens', ['user_id'])
    op.create_index('idx_device_tokens_token', 'user_device_tokens', ['token'])
    op.create_index('idx_device_tokens_active', 'user_device_tokens', ['is_active'])

    # =========================================================================
    # 2. MEDIA FILES - File storage with metadata
    # =========================================================================
    op.create_table(
        'media_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='Uploader'),
        sa.Column('file_type', sa.String(length=20), nullable=False, comment='image, video'),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('file_path', sa.Text(), nullable=False, comment='Relative path from uploads/'),
        sa.Column('file_url', sa.Text(), nullable=False, comment='Full URL for access'),
        sa.Column('thumbnail_url', sa.Text(), nullable=True, comment='Thumbnail URL'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='Size in bytes'),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True, comment='Video duration in seconds'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='EXIF data, location, etc.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_media_user_id', 'media_files', ['user_id'])
    op.create_index('idx_media_file_type', 'media_files', ['file_type'])
    op.create_index('idx_media_created_at', 'media_files', ['created_at'])

    # =========================================================================
    # 3. REPORT MEDIA - Many-to-many relationship
    # =========================================================================
    op.create_table(
        'report_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('media_id', sa.Integer(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0', 
                  comment='Order of images in report'),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['media_id'], ['media_files.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_id', 'media_id', name='uq_report_media')
    )
    op.create_index('idx_report_media_report_id', 'report_media', ['report_id'])
    op.create_index('idx_report_media_media_id', 'report_media', ['media_id'])

    # =========================================================================
    # 4. SENSOR OBSERVATIONS - SOSA/SSN standard observations
    # =========================================================================
    op.create_table(
        'sensor_observations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=False, 
                  comment='URN of sensor entity (NGSI-LD format)'),
        sa.Column('observed_property', sa.String(length=100), nullable=False, 
                  comment='pm25, temperature, humidity, traffic_flow, etc.'),
        sa.Column('result_value', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('result_unit', sa.String(length=50), nullable=True, 
                  comment='μg/m³, °C, %, vehicles/hour'),
        sa.Column('result_quality', sa.String(length=50), nullable=True, 
                  comment='good, moderate, unhealthy, etc.'),
        sa.Column('phenomenon_time', sa.DateTime(timezone=True), nullable=False, 
                  comment='When the observation was made'),
        sa.Column('result_time', sa.DateTime(timezone=True), nullable=True, 
                  comment='When the result was processed'),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, 
                  dimension=2, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='Additional observation metadata'),
        sa.Column('source', sa.String(length=50), nullable=True, 
                  comment='aqicn, openweathermap, tomtom, manual'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_observations_entity', 'sensor_observations', ['entity_id'])
    op.create_index('idx_observations_property', 'sensor_observations', ['observed_property'])
    op.create_index('idx_observations_time', 'sensor_observations', ['phenomenon_time'])
    op.create_index('idx_observations_location', 'sensor_observations', ['location'], 
                    postgresql_using='gist')
    op.create_index('idx_observations_source', 'sensor_observations', ['source'])


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('sensor_observations')
    op.drop_table('report_media')
    op.drop_table('media_files')
    op.drop_table('user_device_tokens')
