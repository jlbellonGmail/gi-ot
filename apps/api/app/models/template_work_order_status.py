import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TemplateWorkOrderStatus(Base):
    """Estado de OT estándar de una `ConfigTemplate`.

    Se copia a `WorkOrderStatus` de cada tenant al provisionarlo
    (`app.core.provisioning`). `code` es la misma semántica interna fija
    del núcleo (PRD §29): la plantilla no introduce códigos adicionales.
    No pertenece a ningún tenant.
    """

    __tablename__ = "template_work_order_statuses"
    __table_args__ = (
        UniqueConstraint(
            "template_id", "code", name="uq_template_work_order_statuses_template_code"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("config_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
