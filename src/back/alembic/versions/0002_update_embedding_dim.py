"""update embedding dim from 1536 (OpenAI) to 384 (sentence-transformers)

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # Recria a coluna embedding com a nova dimensão (384 para MiniLM-L12-v2)
    # Dados anteriores com dimensão 1536 são incompatíveis, então a coluna é
    # descartada e recriada. O seed_sentencas.py deve ser re-executado após.
    conn.execute(sa.text(
        "ALTER TABLE sentenca_historica DROP COLUMN IF EXISTS embedding"
    ))
    conn.execute(sa.text(
        "ALTER TABLE sentenca_historica ADD COLUMN IF NOT EXISTS embedding vector(384)"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE sentenca_historica DROP COLUMN IF EXISTS embedding"
    ))
    conn.execute(sa.text(
        "ALTER TABLE sentenca_historica ADD COLUMN IF NOT EXISTS embedding vector(1536)"
    ))
