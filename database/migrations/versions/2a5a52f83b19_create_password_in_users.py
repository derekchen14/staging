"""Create password in users

Revision ID: 2a5a52f83b19
Revises: cde5755a4def
Create Date: 2023-07-22 09:27:43.283779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a5a52f83b19'
down_revision = 'cde5755a4def'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('_password', sa.String(length=60), nullable=False))


def downgrade() -> None:
    op.drop_column('users', '_password')
