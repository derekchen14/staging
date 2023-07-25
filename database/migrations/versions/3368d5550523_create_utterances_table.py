"""Create utterances table

Revision ID: 3368d5550523
Revises: 273a9c1ed6a3
Create Date: 2023-05-12 19:29:02.917007

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '3368d5550523'
down_revision = '273a9c1ed6a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('utterances',
        sa.Column('utt_id', sa.Integer, primary_key=True),
        sa.Column('short_embed', Vector(384), nullable=False),
        sa.Column('medium_embed', Vector(768)),
        sa.Column('long_embed', Vector(1536)),
        sa.Column('speaker', sa.String(10), nullable=False),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('table_cols', sa.String),
        sa.Column('operations', sa.String),
        sa.Column('aggregation', sa.String),
        sa.Column('dact_id', sa.Integer, sa.ForeignKey('dialogue_acts.dact_id'))
    )

def downgrade() -> None:
    op.drop_table('utterances')