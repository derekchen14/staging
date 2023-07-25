"""build vector index

Revision ID: cde5755a4def
Revises: 3368d5550523
Create Date: 2023-05-16 09:36:25.000114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cde5755a4def'
down_revision = '3368d5550523'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('utterances_ivfflat_idx',
        'utterances',
        ['short_embed'],   # columns to index ['medium_embed', 'long_embed']
        unique=False,
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100},
        postgresql_ops={'embedding': 'vector_cosine_ops'}
    )


def downgrade() -> None:
    op.drop_index('utterances_ivfflat_idx',
        table_name='utterances'
    )