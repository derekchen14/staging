"""Create users table

Revision ID: 85bcf0948473
Revises: 
Create Date: 2023-05-10 07:31:49.427129

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '85bcf0948473'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('user_id', sa.Integer, primary_key=True),
        sa.Column('first', sa.String(), nullable=False),
        sa.Column('middle', sa.String()),
        sa.Column('last', sa.String()),
        sa.Column('email', sa.Unicode(128)),
        sa.Column('username', sa.String(42), unique=True)
    )

def downgrade() -> None:
    op.drop_table('users')