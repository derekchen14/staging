"""Create intents table

Revision ID: 3d130cb355cf
Revises: 95d68d07ead2
Create Date: 2023-05-10 19:28:51.591944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d130cb355cf'
down_revision = '95d68d07ead2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('intents',
        sa.Column('intent_id', sa.Integer, primary_key=True),
        sa.Column('level', sa.String(8), nullable=False),
        sa.Column('intent_name', sa.String(32), nullable=False),
        sa.Column('description', sa.Unicode(128)),
    )


def downgrade() -> None:
    op.drop_table('intents')
