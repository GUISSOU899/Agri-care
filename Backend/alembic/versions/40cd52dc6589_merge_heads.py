"""merge heads

Revision ID: 40cd52dc6589
Revises: 20251225_add_crops_table, 3ad0f54d93d3
Create Date: 2025-12-25 18:00:37.433509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40cd52dc6589'
down_revision = ('20251225_add_crops_table', '3ad0f54d93d3')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
