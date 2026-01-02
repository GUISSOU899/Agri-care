"""add crops table

Revision ID: 20251225_add_crops_table
Revises: 23544eb8ea12
Create Date: 2025-12-25 17:58:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251225_add_crops_table"
down_revision = "23544eb8ea12"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crop",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("variety", sa.String(length=100), nullable=True),
        sa.Column("water_need", sa.Float, nullable=False),
        sa.Column("temp_low", sa.Float, nullable=False),
        sa.Column("temp_high", sa.Float, nullable=False),
        sa.Column("rain_threshold", sa.Float, nullable=False),
        sa.UniqueConstraint("name", name="uq_crop_name"),
    )


def downgrade():
    op.drop_table("crop")
