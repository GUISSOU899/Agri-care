"""add_weather_fields_to_forecast

Revision ID: cc8d885dbd03
Revises: 20251211_add_core_tables
Create Date: 2025-12-13 12:18:01.857991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc8d885dbd03'
down_revision = '20251211_add_core_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('forecast', sa.Column('temperature_c', sa.Float(), nullable=True))
    op.add_column('forecast', sa.Column('rainfall_mm', sa.Float(), nullable=True))
    op.add_column('forecast', sa.Column('evapotranspiration_mm', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('forecast', 'evapotranspiration_mm')
    op.drop_column('forecast', 'rainfall_mm')
    op.drop_column('forecast', 'temperature_c')
