"""receta_id nullable en productos

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-10 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Permite NULL en productos.receta_id (no toca los datos existentes).
    op.alter_column('productos', 'receta_id', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Revertir exige que no haya filas con receta_id NULL.
    op.alter_column('productos', 'receta_id', existing_type=sa.Integer(), nullable=False)
