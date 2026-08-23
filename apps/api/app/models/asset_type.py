import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssetType(Base):
    """Tipo de activo, catálogo parametrizable por tenant (PRD §25).

    Se provisiona copiando `TemplateAssetType` de la plantilla de
    configuración del tenant al crearlo (`app.core.provisioning`), no una
    lista rígida universal: el tenant lo amplía o renombra según su rubro.
    `code` es la semántica interna estable que referencia
    `Asset.asset_type_id`; `label` es la etiqueta visible editable.
    """

    __tablename__ = "asset_types"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_asset_types_tenant_code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
