"""Agrega tablas pedidos y pedido_items

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('pedidos',
    sa.Column('cliente_id', sa.Integer(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('descontado', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pedido_items',
    sa.Column('pedido_id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('precio_unitario', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id'], ),
    sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('pedido_items')
    op.drop_table('pedidos')
