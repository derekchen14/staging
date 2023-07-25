"""Create dacts table

Revision ID: 273a9c1ed6a3
Revises: 3d130cb355cf
Create Date: 2023-05-11 14:17:04.792840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '273a9c1ed6a3'
down_revision = '3d130cb355cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('dialogue_acts',
        sa.Column('dact_id', sa.Integer, primary_key=True),
        sa.Column('dact', sa.String(64), nullable=False),
        sa.Column('dax', sa.String(4), nullable=False),
        sa.Column('description', sa.Unicode(512)),
        sa.Column('intent_id', sa.Integer, sa.ForeignKey('intents.intent_id')),
        sa.Column('agent_id', sa.Integer, sa.ForeignKey('agents.agent_id'))
    )

def downgrade() -> None:
    op.drop_table('dialogue_acts')