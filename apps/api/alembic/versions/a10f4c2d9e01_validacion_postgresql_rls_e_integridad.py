"""validacion PostgreSQL: RLS e integridad tenant

Revision ID: a10f4c2d9e01
Revises: 9c8b2c1d4e5f
Create Date: 2026-08-31

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a10f4c2d9e01"
down_revision: str | Sequence[str] | None = "9c8b2c1d4e5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TENANT_TABLES = (
    "tenant_configs",
    "people",
    "person_identifications",
    "customers",
    "technicians",
    "locations",
    "assets",
    "asset_types",
    "priorities",
    "work_order_statuses",
    "work_order_types",
    "work_orders",
    "work_order_history",
    "work_order_photos",
    "work_order_receipts",
    "sync_operations",
)

_TARGET_UNIQUES = (
    ("users", "uq_users_tenant_id", ("tenant_id", "id")),
    ("locations", "uq_locations_tenant_id", ("tenant_id", "id")),
    ("assets", "uq_assets_tenant_id", ("tenant_id", "id")),
    ("asset_types", "uq_asset_types_tenant_id", ("tenant_id", "id")),
    ("priorities", "uq_priorities_tenant_id", ("tenant_id", "id")),
    (
        "work_order_statuses",
        "uq_work_order_statuses_tenant_id",
        ("tenant_id", "id"),
    ),
    (
        "work_order_types",
        "uq_work_order_types_tenant_id",
        ("tenant_id", "id"),
    ),
)

_TENANT_FOREIGN_KEYS = (
    (
        "person_identifications",
        "fk_person_identifications_tenant_person",
        ("tenant_id", "person_id"),
        "people",
        ("tenant_id", "id"),
        "CASCADE",
    ),
    (
        "assets",
        "fk_assets_tenant_location",
        ("tenant_id", "location_id"),
        "locations",
        ("tenant_id", "id"),
        None,
    ),
    (
        "assets",
        "fk_assets_tenant_asset_type",
        ("tenant_id", "asset_type_id"),
        "asset_types",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_orders",
        "fk_work_orders_tenant_location",
        ("tenant_id", "location_id"),
        "locations",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_orders",
        "fk_work_orders_tenant_asset",
        ("tenant_id", "asset_id"),
        "assets",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_orders",
        "fk_work_orders_tenant_type",
        ("tenant_id", "work_order_type_id"),
        "work_order_types",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_orders",
        "fk_work_orders_tenant_priority",
        ("tenant_id", "priority_id"),
        "priorities",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_orders",
        "fk_work_orders_tenant_status",
        ("tenant_id", "status_id"),
        "work_order_statuses",
        ("tenant_id", "id"),
        None,
    ),
    (
        "work_order_history",
        "fk_work_order_history_tenant_wo",
        ("tenant_id", "work_order_id"),
        "work_orders",
        ("tenant_id", "id"),
        "CASCADE",
    ),
    (
        "work_order_photos",
        "fk_work_order_photos_tenant_wo",
        ("tenant_id", "work_order_id"),
        "work_orders",
        ("tenant_id", "id"),
        "CASCADE",
    ),
    (
        "sync_operations",
        "fk_sync_operations_tenant_wo",
        ("tenant_id", "entity_id"),
        "work_orders",
        ("tenant_id", "id"),
        "SET NULL",
    ),
)


def _inspector() -> sa.Inspector:
    return sa.inspect(op.get_bind())


def _ensure_sync_operations() -> None:
    """Cubre bases ya estampadas donde la tabla se creó fuera de Alembic."""

    if "sync_operations" in _inspector().get_table_names():
        return

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
        sa.ForeignKeyConstraint(["entity_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_operations_tenant_id", "sync_operations", ["tenant_id"])
    op.create_index(
        "ix_sync_ops_tenant_status",
        "sync_operations",
        ["tenant_id", "status", "created_at"],
    )
    op.create_index(
        "ix_sync_ops_tenant_wo",
        "sync_operations",
        ["tenant_id", "entity_id"],
    )


def _ensure_unique(table: str, name: str, columns: tuple[str, ...]) -> None:
    signatures = {
        tuple(item["column_names"])
        for item in _inspector().get_unique_constraints(table)
    }
    if columns in signatures:
        return

    with op.batch_alter_table(table) as batch_op:
        batch_op.create_unique_constraint(name, list(columns))


def _ensure_fk(
    table: str,
    name: str,
    local_columns: tuple[str, ...],
    remote_table: str,
    remote_columns: tuple[str, ...],
    ondelete: str | None,
) -> None:
    for foreign_key in _inspector().get_foreign_keys(table):
        if (
            tuple(foreign_key["constrained_columns"]) == local_columns
            and foreign_key["referred_table"] == remote_table
            and tuple(foreign_key["referred_columns"]) == remote_columns
        ):
            return

    with op.batch_alter_table(table) as batch_op:
        batch_op.create_foreign_key(
            name,
            remote_table,
            list(local_columns),
            list(remote_columns),
            ondelete=ondelete,
        )


def _drop_legacy_global_qr_unique() -> None:
    for constraint in _inspector().get_unique_constraints("assets"):
        if tuple(constraint["column_names"]) != ("qr_code",):
            continue
        name = constraint.get("name")
        naming_convention = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
        with op.batch_alter_table(
            "assets", naming_convention=naming_convention
        ) as batch_op:
            batch_op.drop_constraint(name or "uq_assets_qr_code", type_="unique")


def _tenant_scope(column: str = "tenant_id") -> str:
    platform = (
        "COALESCE(NULLIF(current_setting('app.platform_admin', true), '')"
        "::boolean, false)"
    )
    tenant = f"{column} = NULLIF(current_setting('app.tenant_id', true), '')::uuid"
    return f"({platform} OR {tenant})"


def _enable_rls() -> None:
    for table in _TENANT_TABLES:
        scope = _tenant_scope()
        op.execute(sa.text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'DROP POLICY IF EXISTS tenant_isolation ON "{table}"'))
        op.execute(
            sa.text(
                f'CREATE POLICY tenant_isolation ON "{table}" FOR ALL '
                f"USING ({scope}) WITH CHECK ({scope})"
            )
        )

    tenant_scope = _tenant_scope("id")
    op.execute(sa.text('ALTER TABLE "tenants" ENABLE ROW LEVEL SECURITY'))
    op.execute(sa.text('ALTER TABLE "tenants" FORCE ROW LEVEL SECURITY'))
    op.execute(sa.text('DROP POLICY IF EXISTS tenant_isolation ON "tenants"'))
    op.execute(
        sa.text(
            'CREATE POLICY tenant_isolation ON "tenants" FOR ALL '
            f"USING ({tenant_scope}) WITH CHECK ({tenant_scope})"
        )
    )

    user_scope = _tenant_scope()
    user_id_scope = "id = NULLIF(current_setting('app.user_id', true), '')::uuid"
    login_scope = (
        "lower(email) = lower(NULLIF(current_setting('app.login_email', true), ''))"
    )
    op.execute(sa.text('ALTER TABLE "users" ENABLE ROW LEVEL SECURITY'))
    op.execute(sa.text('ALTER TABLE "users" FORCE ROW LEVEL SECURITY'))
    for policy in (
        "users_select",
        "users_insert",
        "users_update",
        "users_delete",
    ):
        op.execute(sa.text(f'DROP POLICY IF EXISTS {policy} ON "users"'))
    op.execute(
        sa.text(
            'CREATE POLICY users_select ON "users" FOR SELECT '
            f"USING ({user_scope} OR {user_id_scope} OR {login_scope})"
        )
    )
    op.execute(
        sa.text(
            'CREATE POLICY users_insert ON "users" FOR INSERT '
            f"WITH CHECK ({user_scope})"
        )
    )
    op.execute(
        sa.text(
            'CREATE POLICY users_update ON "users" FOR UPDATE '
            f"USING ({user_scope}) WITH CHECK ({user_scope})"
        )
    )
    op.execute(
        sa.text(
            f'CREATE POLICY users_delete ON "users" FOR DELETE USING ({user_scope})'
        )
    )


def upgrade() -> None:
    _ensure_sync_operations()

    columns = {
        column["name"] for column in _inspector().get_columns("work_order_statuses")
    }
    if "sort_order" not in columns:
        with op.batch_alter_table("work_order_statuses") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "sort_order",
                    sa.Integer(),
                    nullable=False,
                    server_default=sa.text("0"),
                )
            )

    _drop_legacy_global_qr_unique()

    # Reparaciones de constraints requeridas por FKs históricas PostgreSQL.
    _ensure_unique("people", "uq_people_tenant_id", ("tenant_id", "id"))
    _ensure_unique("work_orders", "uq_work_orders_tenant_id", ("tenant_id", "id"))
    for table, name, columns in _TARGET_UNIQUES:
        _ensure_unique(table, name, columns)
    for foreign_key in _TENANT_FOREIGN_KEYS:
        _ensure_fk(*foreign_key)

    if op.get_bind().dialect.name == "postgresql":
        _enable_rls()


def _disable_rls() -> None:
    for table in (*_TENANT_TABLES, "tenants"):
        op.execute(sa.text(f'DROP POLICY IF EXISTS tenant_isolation ON "{table}"'))
        op.execute(sa.text(f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY'))

    for policy in (
        "users_select",
        "users_insert",
        "users_update",
        "users_delete",
    ):
        op.execute(sa.text(f'DROP POLICY IF EXISTS {policy} ON "users"'))
    op.execute(sa.text('ALTER TABLE "users" NO FORCE ROW LEVEL SECURITY'))
    op.execute(sa.text('ALTER TABLE "users" DISABLE ROW LEVEL SECURITY'))


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        _disable_rls()

    for table, name, *_rest in reversed(_TENANT_FOREIGN_KEYS):
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_constraint(name, type_="foreignkey")

    for table, name, _columns in reversed(_TARGET_UNIQUES):
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_constraint(name, type_="unique")

    with op.batch_alter_table("work_order_statuses") as batch_op:
        batch_op.drop_column("sort_order")
