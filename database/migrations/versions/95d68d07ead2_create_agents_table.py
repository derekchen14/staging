"""Create agents table

Revision ID: 95d68d07ead2
Revises: 85bcf0948473
Create Date: 2023-05-10 07:46:21.165856

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '95d68d07ead2'
down_revision = '85bcf0948473'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agents',
        sa.Column('agent_id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('use_case', sa.String(), unique=True)
    )

def downgrade() -> None:
    op.drop_table('agents')
