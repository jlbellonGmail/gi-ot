"""etapa 09c: agregar branding a tenant_configs + fix sync_operation index

Revision ID: 9c8b2c1d4e5f
Revises: 7f8a9b2c1d4e
Create Date: 2024-08-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '9c8b2c1d4e5f'
down_revision = '7f8a9b2c1d4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'tenant_configs' in tables:
        # Agregar columnas de branding a tenant_configs solo si no existen
        columns = [col['name'] for col in inspector.get_columns('tenant_configs')]
        
        branding_columns = {
            'logo_url': sa.Column('logo_url', sa.String(length=500), nullable=True),
            'primary_color': sa.Column('primary_color', sa.String(length=20), nullable=True, server_default='#0f172a'),
            'secondary_color': sa.Column('secondary_color', sa.String(length=20), nullable=True, server_default='#1e293b'),
            'address': sa.Column('address', sa.Text(), nullable=True),
            'phone': sa.Column('phone', sa.String(length=50), nullable=True),
            'email': sa.Column('email', sa.String(length=120), nullable=True),
            'website': sa.Column('website', sa.String(length=200), nullable=True),
            'tax_id': sa.Column('tax_id', sa.String(length=50), nullable=True),
        }
        
        for col_name, col in branding_columns.items():
            if col_name not in columns:
                op.add_column('tenant_configs', col)
    
    # Fix sync_operation index - only if table exists
    if 'sync_operations' in inspector.get_table_names():
        indexes = inspector.get_indexes('sync_operations')
        index_names = [idx['name'] for idx in inspector.get_indexes('sync_operations')]
        
        if 'ix_sync_ops_tenant_wo' in index_names:
            op.drop_index('ix_sync_ops_tenant_wo', table_name='sync_operations')
        
        # Create new index on entity_id
        op.create_index(
            'ix_sync_ops_tenant_wo',
            'sync_operations',
            ['tenant_id', 'entity_id'],
            unique=False
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'sync_operations' in tables:
        indexes = inspector.get_indexes('sync_operations')
        index_names = [idx['name'] for idx in inspector.get_indexes('sync_operations')]
        
        if 'ix_sync_ops_tenant_wo' in index_names:
            op.drop_index('ix_sync_ops_tenant_wo', table_name='sync_operations')
        
        # Recreate old index on work_order_id
        op.create_index(
            'ix_sync_ops_tenant_wo',
            'sync_operations',
            ['tenant_id', 'work_order_id'],
            unique=False
        )
    
    if 'tenant_configs' in tables:
        columns = [col['name'] for col in inspector.get_columns('tenant_configs')]
        for col in ['tax_id', 'website', 'email', 'phone', 'address', 'secondary_color', 'primary_color', 'logo_url']:
            if col in columns:
                op.drop_column('tenant_configs', col)