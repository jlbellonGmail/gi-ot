import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TemplatePriority(Base):
    """Prioridad estándar de una `ConfigTemplate`.

    Se copia a `Priority` de cada tenant al provisionarlo
    (`app.core.provisioning`). No pertenece a ningún tenant.
    """

    __tablename__ = "template_priorities"
    __table_args__ = (
        UniqueConstraint("template_id", "code", name="uq_template_priorities_template_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("config_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
