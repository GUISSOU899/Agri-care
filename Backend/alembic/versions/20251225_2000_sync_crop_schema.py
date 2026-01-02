"""sync crop schema

Revision ID: 20251225_2000_sync_crop
Revises: 40cd52dc6589
Create Date: 2025-12-25 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '20251225_2000_sync_crop'
down_revision = '40cd52dc6589'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [c['name'] for c in inspector.get_columns('crop')]
    
    # 1. Drop old indexes and columns if they exist
    # Note: Alembic operations can be conditional but usually we assume fixed state based on revision history.
    # Since we know we are fixing a specific divergent state where 'crop' comes from 20251211...
    
    # Check if 'code' exists to avoid error if it was already dropped or never existed (defensive)
    if 'code' in columns:
        try:
            op.drop_index('ix_crop_code', table_name='crop')
        except:
            pass # Index might be named differently or missing
        op.drop_column('crop', 'code')

    if 'description' in columns:
        op.drop_column('crop', 'description')

    # 2. Add new columns if they don't exist
    if 'type' not in columns:
        op.add_column('crop', sa.Column('type', sa.String(length=50), nullable=False, server_default='unknown'))
        # Remove default after creation if strict
        # op.alter_column('crop', 'type', server_default=None)

    if 'variety' not in columns:
        op.add_column('crop', sa.Column('variety', sa.String(length=100), nullable=True))

    if 'water_need' not in columns:
        op.add_column('crop', sa.Column('water_need', sa.Float(), nullable=False, server_default='1'))

    if 'temp_low' not in columns:
        op.add_column('crop', sa.Column('temp_low', sa.Float(), nullable=False, server_default='0'))

    if 'temp_high' not in columns:
        op.add_column('crop', sa.Column('temp_high', sa.Float(), nullable=False, server_default='50'))

    if 'rain_threshold' not in columns:
        op.add_column('crop', sa.Column('rain_threshold', sa.Float(), nullable=False, server_default='0'))
    
    # 3. Ensure unique name constraint
    # We might need to handle existing duplicates or name clashes if any
    try:
        op.create_unique_constraint('uq_crop_name', 'crop', ['name'])
    except:
        pass # Constraint might already exist

def downgrade():
    # Revert changes (approximate, assuming we go back to 'code' based schema)
    op.drop_constraint('uq_crop_name', 'crop', type_='unique')
    
    op.drop_column('crop', 'rain_threshold')
    op.drop_column('crop', 'temp_high')
    op.drop_column('crop', 'temp_low')
    op.drop_column('crop', 'water_need')
    op.drop_column('crop', 'variety')
    op.drop_column('crop', 'type')
    
    op.add_column('crop', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('crop', sa.Column('code', sa.String(length=20), nullable=False, server_default='temp'))
    op.create_index('ix_crop_code', 'crop', ['code'], unique=True)
