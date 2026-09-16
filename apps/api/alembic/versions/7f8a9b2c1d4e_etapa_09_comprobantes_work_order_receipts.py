"""etapa 09: comprobantes work_order_receipts + fix sync_operation index

Revision ID: 7f8a9b2c1d4e
Revises: 6d1d48d98e24
Create Date: 2024-08-27

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '7f8a9b2c1d4e'
down_revision = '6d1d48d98e24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Punto 08 introdujo SyncOperation mediante create_all(), pero no dejó una
    # revisión Alembic. Esta revisión es el primer punto histórico que debe
    # materializar el esquema ejecutable respaldado por Git en ese momento.
    op.create_table(
        "sync_operations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("operation_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["work_orders.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sync_operations_tenant_id", "sync_operations", ["tenant_id"]
    )
    op.create_index(
        "ix_sync_ops_tenant_status",
        "sync_operations",
        ["tenant_id", "status", "created_at"],
    )
    op.create_index(
        "ix_sync_ops_tenant_wo", "sync_operations", ["tenant_id", "entity_id"]
    )

    # Crear tabla work_order_receipts
    op.create_table(
        'work_order_receipts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('work_order_id', sa.Uuid(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=False),
        sa.Column('pdf_storage_key', sa.String(length=500), nullable=True),
        sa.Column('generated_by', sa.Uuid(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('sent_to_email', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sent_to_whatsapp', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('last_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['generated_by'], ['users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['tenant_id', 'work_order_id'],
            ['work_orders.tenant_id', 'work_orders.id'],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_wor_receipt_tenant_wo',
        'work_order_receipts',
        ['tenant_id', 'work_order_id'],
        unique=False
    )
    op.create_index(
        "ix_work_order_receipts_tenant_id", "work_order_receipts", ["tenant_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_work_order_receipts_tenant_id", table_name="work_order_receipts")
    op.drop_index('ix_wor_receipt_tenant_wo', table_name='work_order_receipts')
    op.drop_table('work_order_receipts')
    op.drop_index('ix_sync_ops_tenant_wo', table_name='sync_operations')
    op.drop_index('ix_sync_ops_tenant_status', table_name='sync_operations')
    op.drop_index('ix_sync_operations_tenant_id', table_name='sync_operations')
    op.drop_table('sync_operations')
