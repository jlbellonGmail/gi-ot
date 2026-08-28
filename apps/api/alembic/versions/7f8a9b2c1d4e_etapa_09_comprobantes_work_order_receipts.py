"""etapa 09: comprobantes work_order_receipts + fix sync_operation index

Revision ID: 7f8a9b2c1d4e
Revises: 6d1d48d98e24
Create Date: 2024-08-27

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '7f8a9b2c1d4e'
down_revision = '6d1d48d98e24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla work_order_receipts
    op.create_table(
        'work_order_receipts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('work_order_id', sa.UUID(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=False),
        sa.Column('pdf_storage_key', sa.String(length=500), nullable=True),
        sa.Column('generated_by', sa.UUID(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('sent_to_email', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('sent_to_whatsapp', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['generated_by'], ['users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['tenant_id', 'work_order_id'],
            ['work_orders.tenant_id', 'work_orders.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_wor_receipt_tenant_wo',
        'work_order_receipts',
        ['tenant_id', 'work_order_id'],
        unique=False
    )

    # Fix: eliminar índice incorrecto en sync_operations y crear el correcto
    op.drop_index('ix_sync_ops_tenant_wo', table_name='sync_operations')
    op.create_index(
        'ix_sync_ops_tenant_wo',
        'sync_operations',
        ['tenant_id', 'entity_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_sync_ops_tenant_wo', table_name='sync_operations')
    op.create_index(
        'ix_sync_ops_tenant_wo',
        'sync_operations',
        ['tenant_id', 'work_order_id'],
        unique=False
    )
    op.drop_index('ix_wor_receipt_tenant_wo', table_name='work_order_receipts')
    op.drop_table('work_order_receipts')