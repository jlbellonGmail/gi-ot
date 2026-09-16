"""Reparación forward de estados históricos de SyncOperation.

Punto 08 creó el modelo fuera de Alembic. 7f materializa el esquema para
nuevas instalaciones; esta revisión normaliza bases que ya tenían la cadena
versionada pero no tenían la tabla o sus índices completos.

La revisión es conservadora: crea sólo estructuras ausentes, nunca elimina
datos ni columnas, y falla explícitamente ante columnas obligatorias ausentes
que no pueden inferirse sin inventar datos.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a10f2c3d4e5f"
down_revision: str | Sequence[str] | None = "9c8b2c1d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _create_table() -> None:
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


def _ensure_indexes(inspector: sa.Inspector) -> None:
    indexes = {item["name"] for item in inspector.get_indexes("sync_operations")}
    definitions = (
        ("ix_sync_operations_tenant_id", ("tenant_id",)),
        ("ix_sync_ops_tenant_status", ("tenant_id", "status", "created_at")),
        ("ix_sync_ops_tenant_wo", ("tenant_id", "entity_id")),
    )
    for name, columns in definitions:
        if name not in indexes:
            op.create_index(name, "sync_operations", list(columns), unique=False)


def _ensure_foreign_keys(inspector: sa.Inspector) -> None:
    foreign_keys = inspector.get_foreign_keys("sync_operations")
    signatures = {
        (
            tuple(item["constrained_columns"]),
            item["referred_table"],
            tuple(item["referred_columns"]),
        )
        for item in foreign_keys
    }
    missing = []
    if (("tenant_id",), "tenants", ("id",)) not in signatures:
        missing.append(
            (
                "fk_sync_operations_tenant",
                ["tenant_id"],
                "tenants",
                ["id"],
                "CASCADE",
            )
        )
    if (("entity_id",), "work_orders", ("id",)) not in signatures:
        missing.append(
            (
                "fk_sync_operations_entity",
                ["entity_id"],
                "work_orders",
                ["id"],
                "SET NULL",
            )
        )
    if missing:
        with op.batch_alter_table("sync_operations") as batch_op:
            for name, columns, remote_table, remote_columns, ondelete in missing:
                batch_op.create_foreign_key(
                    name,
                    remote_table,
                    columns,
                    remote_columns,
                    ondelete=ondelete,
                )


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "sync_operations" not in inspector.get_table_names():
        _create_table()
        inspector = sa.inspect(op.get_bind())
    else:
        columns = {item["name"] for item in inspector.get_columns("sync_operations")}
        required = {
            "id",
            "tenant_id",
            "operation_type",
            "entity_id",
            "payload",
            "status",
            "attempt",
            "max_attempts",
            "created_at",
            "synced_at",
        }
        missing = sorted(required - columns)
        if missing:
            raise RuntimeError(
                "sync_operations tiene columnas obligatorias ausentes; "
                f"reparación no destructiva no inferible: {missing}"
            )
    _ensure_indexes(inspector)
    _ensure_foreign_keys(sa.inspect(op.get_bind()))


def downgrade() -> None:
    # Reparación forward deliberadamente no destructiva. No elimina una tabla
    # que pudo existir antes de esta revisión ni arriesga pérdida de datos.
    pass
