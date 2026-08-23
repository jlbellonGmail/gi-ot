import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset_type import AssetType
from app.models.config_template import DEFAULT_TEMPLATE_CODE, ConfigTemplate
from app.models.priority import Priority
from app.models.template_asset_type import TemplateAssetType
from app.models.template_priority import TemplatePriority
from app.models.template_work_order_status import TemplateWorkOrderStatus
from app.models.template_work_order_type import TemplateWorkOrderType
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType


class ConfigTemplateNotFound(Exception):
    """No existe una `ConfigTemplate` activa con el `code` solicitado."""


def _copy_missing(db: Session, template_model, tenant_model, template_id: uuid.UUID, tenant_id: uuid.UUID, build) -> None:
    """Copia a `tenant_model` las filas de `template_model` cuyo `code`
    todavía no existe para ese tenant.

    Hace que el provisionamiento sea idempotente: reejecutarlo sobre un
    tenant ya inicializado no duplica registros (ROADMAP.md §02). Las filas
    copiadas son propias del tenant (nueva fila, nuevo `id`) — nunca una
    referencia a la plantilla — de modo que personalizarlas después nunca
    modifica la plantilla ni otro tenant.
    """
    template_rows = db.scalars(
        select(template_model).where(template_model.template_id == template_id)
    ).all()
    if not template_rows:
        return

    existing_codes = set(db.scalars(select(tenant_model.code).where(tenant_model.tenant_id == tenant_id)))
    for row in template_rows:
        if row.code in existing_codes:
            continue
        db.add(build(row))


def provision_tenant_from_template(
    db: Session, tenant_id: uuid.UUID, template_code: str = DEFAULT_TEMPLATE_CODE
) -> None:
    """Copia a la configuración propia del tenant los valores estándar de
    una `ConfigTemplate` (estados de OT, prioridades, tipos de trabajo,
    tipos de activo).

    Se invoca al crear un tenant nuevo. Es idempotente: puede reejecutarse
    sobre el mismo tenant sin duplicar filas. La plantilla en sí nunca se
    modifica ni se referencia desde el tenant — solo se copian sus valores
    (modelo-datos.md §6).
    """
    template = db.scalar(
        select(ConfigTemplate).where(ConfigTemplate.code == template_code, ConfigTemplate.active.is_(True))
    )
    if template is None:
        raise ConfigTemplateNotFound(f"No existe una plantilla de configuración activa '{template_code}'")

    _copy_missing(
        db,
        TemplatePriority,
        Priority,
        template.id,
        tenant_id,
        lambda row: Priority(tenant_id=tenant_id, code=row.code, label=row.label, sort_order=row.sort_order),
    )

    _copy_missing(
        db,
        TemplateWorkOrderType,
        WorkOrderType,
        template.id,
        tenant_id,
        lambda row: WorkOrderType(tenant_id=tenant_id, code=row.code, label=row.label),
    )

    _copy_missing(
        db,
        TemplateWorkOrderStatus,
        WorkOrderStatus,
        template.id,
        tenant_id,
        lambda row: WorkOrderStatus(
            tenant_id=tenant_id, code=row.code, label=row.label, is_terminal=row.is_terminal
        ),
    )

    _copy_missing(
        db,
        TemplateAssetType,
        AssetType,
        template.id,
        tenant_id,
        lambda row: AssetType(tenant_id=tenant_id, code=row.code, label=row.label),
    )
