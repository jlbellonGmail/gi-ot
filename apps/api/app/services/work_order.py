"""Capa de servicio/dominio para el módulo WorkOrder (Etapa 04 — ROADMAP.md §04).

Implementa la máquina de estados completa de la OT, validaciones multitenant,
generación correlativa de número, y grabación automática de historial en
work_order_history (§4.17 modelo-datos.md).

El `tenant_id` de contexto siempre llega como parámetro explícito desde el
router (resuelto server-side vía `get_current_tenant_id`), nunca se resuelve
dentro del servicio (mismo patrón que `PersonService`).
"""

import mimetypes
import uuid as uuid_module
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.core.config import get_settings
from app.enums import HistoryEventType
from app.exceptions import (
    InvalidTransition,
    RefValidationError,
    TechnicianNotFound,
    TechnicianNotLinked,
    TerminalWorkOrder,
    WorkOrderNotFound,
)
from app.models.location import Asset, Location
from app.models.person import Customer, Person, Technician
from app.models.priority import Priority
from app.models.work_order import WorkOrder, WorkOrderHistory, WorkOrderPhoto
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderFinish,
    WorkOrderReopen,
    WorkOrderUpdate,
)

# Extensiones de imagen aceptadas para fotos de OT (ROADMAP §06 — Fotografías).
_ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
_MAX_PHOTO_SIZE_BYTES = 10 * 1024 * 1024

_ALLOWED_TRANSITIONS = {
    "PENDING": {"IN_PROGRESS"},
    "IN_PROGRESS": {"COMPLETED", "UNRESOLVED"},
    "COMPLETED": set(),
    "UNRESOLVED": set(),
}


class WorkOrderService:
    """Servicio de dominio para operaciones sobre OT con máquina de estados."""

    def __init__(self, db: Session):
        self.db = db

    # ── Helpers internos ─────────────────────────────────────────────

    def _status_id_by_code(self, tenant_id: UUID, code: str) -> UUID:
        status_id = self.db.execute(
            select(WorkOrderStatus.id).where(
                WorkOrderStatus.tenant_id == tenant_id, WorkOrderStatus.code == code
            )
        ).scalar_one_or_none()
        if status_id is None:
            raise RefValidationError("status")
        return status_id

    def _check_transition(self, current_code: str, target_code: str) -> None:
        if target_code not in _ALLOWED_TRANSITIONS.get(current_code, set()):
            raise InvalidTransition(current_code, target_code)

    def _next_number(self, tenant_id: UUID) -> int:
        max_val = self.db.execute(
            select(func.max(WorkOrder.number)).where(WorkOrder.tenant_id == tenant_id)
        ).scalar()
        return (max_val or 0) + 1

    def _add_history(
        self,
        tenant_id: UUID,
        wo_id: UUID,
        event_type: HistoryEventType,
        performed_by: Optional[UUID],
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        self.db.add(
            WorkOrderHistory(
                tenant_id=tenant_id,
                work_order_id=wo_id,
                event_type=event_type,
                previous_value=previous_value,
                new_value=new_value,
                performed_by=performed_by,
                notes=notes,
            )
        )

    def _validate_tenant_refs(
        self,
        tenant_id: UUID,
        customer_id: UUID,
        location_id: UUID,
        asset_id: UUID,
        work_order_type_id: UUID,
        priority_id: UUID,
        technician_id: Optional[UUID],
    ) -> None:
        """Valida que todas las FK pertenecen al mismo tenant (y jerarquía
        correcta customer → location → asset) antes de persistir."""
        customer = self.db.get(Customer, (tenant_id, customer_id))
        if customer is None:
            raise RefValidationError("customer")

        location = self.db.get(Location, location_id)
        if location is None or location.tenant_id != tenant_id:
            raise RefValidationError("location")
        if location.customer_id != customer_id:
            raise RefValidationError("location belongs to different customer")

        asset = self.db.get(Asset, asset_id)
        if asset is None or asset.tenant_id != tenant_id:
            raise RefValidationError("asset")
        if asset.location_id != location_id:
            raise RefValidationError("asset belongs to different location")

        work_order_type = self.db.get(WorkOrderType, work_order_type_id)
        if work_order_type is None or work_order_type.tenant_id != tenant_id:
            raise RefValidationError("work_order_type")

        priority = self.db.get(Priority, priority_id)
        if priority is None or priority.tenant_id != tenant_id:
            raise RefValidationError("priority")

        if technician_id is not None:
            technician = self.db.get(Technician, (tenant_id, technician_id))
            if technician is None:
                raise TechnicianNotFound(str(technician_id))

    # ── Crear OT ──────────────────────────────────────────────────────

    def create_wo(self, tenant_id: UUID, payload: WorkOrderCreate, created_by: UUID) -> WorkOrder:
        self._validate_tenant_refs(
            tenant_id,
            customer_id=payload.customer_id,
            location_id=payload.location_id,
            asset_id=payload.asset_id,
            work_order_type_id=payload.work_order_type_id,
            priority_id=payload.priority_id,
            technician_id=payload.technician_id,
        )

        wo = WorkOrder(
            tenant_id=tenant_id,
            number=self._next_number(tenant_id),
            customer_id=payload.customer_id,
            location_id=payload.location_id,
            asset_id=payload.asset_id,
            technician_id=payload.technician_id,
            work_order_type_id=payload.work_order_type_id,
            priority_id=payload.priority_id,
            status_id=self._status_id_by_code(tenant_id, "PENDING"),
            requested_description=payload.requested_description,
            scheduled_at=payload.scheduled_at,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(wo)
        self.db.flush()

        self._add_history(
            tenant_id, wo.id, HistoryEventType.CREATED, performed_by=created_by, new_value="PENDING"
        )
        if payload.technician_id is not None:
            self._add_history(
                tenant_id,
                wo.id,
                HistoryEventType.ASSIGNED,
                performed_by=created_by,
                new_value=str(payload.technician_id),
            )

        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Crear OT urgente (técnico, desde campo) ──────────────────────

    def create_wo_as_technician(
        self, tenant_id: UUID, payload: WorkOrderCreate, technician_user_id: UUID, created_by: UUID
    ) -> WorkOrder:
        """Crea una OT urgente iniciada por el propio técnico en campo
        (PRD §20). Prioridad y técnico asignado se fuerzan en backend,
        ignorando cualquier valor recibido en el payload para esos campos:
        prioridad = URGENT, técnico = el vinculado al User autenticado."""
        technician = self.db.scalar(
            select(Technician).where(
                Technician.tenant_id == tenant_id, Technician.user_id == technician_user_id
            )
        )
        if technician is None:
            raise TechnicianNotLinked()

        urgent_priority_id = self.db.scalar(
            select(Priority.id).where(Priority.tenant_id == tenant_id, Priority.code == "URGENT")
        )
        if urgent_priority_id is None:
            raise RefValidationError("priority")

        forced_payload = payload.model_copy(
            update={"priority_id": urgent_priority_id, "technician_id": technician.person_id}
        )
        return self.create_wo(tenant_id, forced_payload, created_by=created_by)

    # ── Obtener / listar OT ──────────────────────────────────────────

    def get_wo(self, tenant_id: UUID, wo_id: UUID) -> WorkOrder:
        wo = self.db.get(WorkOrder, wo_id)
        if wo is None or wo.tenant_id != tenant_id:
            raise WorkOrderNotFound(str(wo_id))
        return wo

    def list_wo(
        self,
        tenant_id: UUID,
        status_code: Optional[str] = None,
        technician_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        priority_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
        asset_id: Optional[UUID] = None,
        q: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort: Optional[str] = None,
    ) -> List[WorkOrder]:
        """Listado operativo de OT (ROADMAP §07): búsqueda, filtros y
        ordenamiento se combinan libremente sobre el mismo resultado
        (UI-UX-STANDARDS.md §10) — ningún criterio pisa a los demás.
        """
        stmt = select(WorkOrder).where(WorkOrder.tenant_id == tenant_id)

        if status_code:
            stmt = stmt.where(WorkOrder.status_id == self._status_id_by_code(tenant_id, status_code))
        if technician_id is not None:
            stmt = stmt.where(WorkOrder.technician_id == technician_id)
        if customer_id is not None:
            stmt = stmt.where(WorkOrder.customer_id == customer_id)
        if priority_id is not None:
            stmt = stmt.where(WorkOrder.priority_id == priority_id)
        if location_id is not None:
            stmt = stmt.where(WorkOrder.location_id == location_id)
        if asset_id is not None:
            stmt = stmt.where(WorkOrder.asset_id == asset_id)
        if date_from is not None:
            stmt = stmt.where(WorkOrder.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(WorkOrder.created_at <= date_to)

        if q:
            like = f"%{q.strip()}%"
            customer_person = aliased(Person)
            stmt = (
                stmt.outerjoin(customer_person, WorkOrder.customer_id == customer_person.id)
                .outerjoin(Location, WorkOrder.location_id == Location.id)
                .outerjoin(Asset, WorkOrder.asset_id == Asset.id)
                .where(
                    or_(
                        cast(WorkOrder.number, String).ilike(like),
                        customer_person.display_name.ilike(like),
                        Location.name.ilike(like),
                        Asset.name.ilike(like),
                        WorkOrder.requested_description.ilike(like),
                    )
                )
            )

        if sort == "date_asc":
            stmt = stmt.order_by(WorkOrder.created_at.asc())
        elif sort == "priority":
            stmt = stmt.join(Priority, WorkOrder.priority_id == Priority.id).order_by(
                Priority.sort_order.desc(), WorkOrder.created_at.desc()
            )
        elif sort == "updated":
            stmt = stmt.order_by(WorkOrder.updated_at.desc())
        elif sort == "status":
            stmt = stmt.join(WorkOrderStatus, WorkOrder.status_id == WorkOrderStatus.id).order_by(
                WorkOrderStatus.code.asc(), WorkOrder.created_at.desc()
            )
        else:
            stmt = stmt.order_by(WorkOrder.created_at.desc())

        return list(self.db.scalars(stmt))

    # ── Actualizar OT (campos no ejecutivos) ─────────────────────────

    def update_wo(self, tenant_id: UUID, wo_id: UUID, payload: WorkOrderUpdate) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)
        if wo.status.is_terminal:
            raise TerminalWorkOrder(wo.status.code)

        if payload.requested_description is not None:
            wo.requested_description = payload.requested_description
        if payload.scheduled_at is not None:
            wo.scheduled_at = payload.scheduled_at
        if payload.work_order_type_id is not None:
            wot = self.db.get(WorkOrderType, payload.work_order_type_id)
            if wot is None or wot.tenant_id != tenant_id:
                raise RefValidationError("work_order_type")
            wo.work_order_type_id = payload.work_order_type_id
        if payload.priority_id is not None:
            pri = self.db.get(Priority, payload.priority_id)
            if pri is None or pri.tenant_id != tenant_id:
                raise RefValidationError("priority")
            wo.priority_id = payload.priority_id

        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Asignar técnico ───────────────────────────────────────────────

    def assign_technician(
        self, tenant_id: UUID, wo_id: UUID, technician_id: UUID, performed_by: UUID
    ) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)
        if wo.status.is_terminal:
            raise TerminalWorkOrder(wo.status.code)

        technician = self.db.get(Technician, (tenant_id, technician_id))
        if technician is None:
            raise TechnicianNotFound(str(technician_id))

        previous = str(wo.technician_id) if wo.technician_id else None
        wo.technician_id = technician_id
        wo.updated_by = performed_by

        self._add_history(
            tenant_id,
            wo.id,
            HistoryEventType.ASSIGNED,
            performed_by=performed_by,
            previous_value=previous,
            new_value=str(technician_id),
        )
        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Iniciar OT ────────────────────────────────────────────────────

    def start_wo(self, tenant_id: UUID, wo_id: UUID, performed_by: UUID) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)

        old_code = wo.status.code
        self._check_transition(old_code, "IN_PROGRESS")

        wo.status_id = self._status_id_by_code(tenant_id, "IN_PROGRESS")
        wo.started_at = datetime.now(timezone.utc)
        wo.updated_by = performed_by

        self._add_history(
            tenant_id,
            wo.id,
            HistoryEventType.STATUS_CHANGE,
            performed_by=performed_by,
            previous_value=old_code,
            new_value="IN_PROGRESS",
        )
        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Registrar trabajo realizado (mientras está en curso) ──────────

    def register_work(
        self, tenant_id: UUID, wo_id: UUID, performed_description: str, performed_by: UUID
    ) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)
        if wo.status.is_terminal:
            raise TerminalWorkOrder(wo.status.code)

        wo.performed_description = performed_description
        wo.updated_by = performed_by
        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Finalizar OT ────────────────────────────────────────────────────

    def finish_wo(self, tenant_id: UUID, wo_id: UUID, payload: WorkOrderFinish, performed_by: UUID) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)

        old_code = wo.status.code
        self._check_transition(old_code, payload.status_code)

        wo.status_id = self._status_id_by_code(tenant_id, payload.status_code)
        wo.finished_at = datetime.now(timezone.utc)
        if payload.performed_description is not None:
            wo.performed_description = payload.performed_description
        wo.updated_by = performed_by

        self._add_history(
            tenant_id,
            wo.id,
            HistoryEventType.STATUS_CHANGE,
            performed_by=performed_by,
            previous_value=old_code,
            new_value=payload.status_code,
        )
        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Reapertura controlada ─────────────────────────────────────────

    def reopen_wo(self, tenant_id: UUID, wo_id: UUID, payload: WorkOrderReopen, performed_by: UUID) -> WorkOrder:
        wo = self.get_wo(tenant_id, wo_id)

        if not wo.status.is_terminal:
            raise InvalidTransition(wo.status.code, "PENDING")

        old_code = wo.status.code
        wo.status_id = self._status_id_by_code(tenant_id, "PENDING")
        wo.started_at = None
        wo.finished_at = None
        wo.updated_by = performed_by

        self._add_history(
            tenant_id,
            wo.id,
            HistoryEventType.REOPENED,
            performed_by=performed_by,
            previous_value=old_code,
            new_value="PENDING",
            notes=payload.notes,
        )
        self.db.commit()
        self.db.refresh(wo)
        return wo

    # ── Historial ─────────────────────────────────────────────────────

    def get_history(self, tenant_id: UUID, wo_id: UUID) -> List[WorkOrderHistory]:
        self.get_wo(tenant_id, wo_id)  # valida existencia + tenant
        stmt = (
            select(WorkOrderHistory)
            .where(WorkOrderHistory.work_order_id == wo_id, WorkOrderHistory.tenant_id == tenant_id)
            .order_by(WorkOrderHistory.performed_at.desc())
        )
        return list(self.db.scalars(stmt))

    # ── Fotografías ────────────────────────────────────────────────────
    # Filesystem local en BOOTSTRAP (decisiones-producto.md §15): la base
    # solo guarda `storage_key`, nunca el binario (arquitectura.md §7).

    def _uploads_root(self) -> Path:
        return Path(get_settings().uploads_dir)

    def add_photo(
        self,
        tenant_id: UUID,
        wo_id: UUID,
        file_bytes: bytes,
        content_type: Optional[str],
        caption: Optional[str],
        uploaded_by: UUID,
    ) -> WorkOrderPhoto:
        wo = self.get_wo(tenant_id, wo_id)
        if wo.status.is_terminal:
            raise TerminalWorkOrder(wo.status.code)

        if content_type not in _ALLOWED_PHOTO_CONTENT_TYPES:
            raise RefValidationError("content_type")
        if len(file_bytes) > _MAX_PHOTO_SIZE_BYTES:
            raise RefValidationError("file_size")

        extension = mimetypes.guess_extension(content_type) or ".jpg"
        relative_path = Path(str(tenant_id)) / str(wo_id) / f"{uuid_module.uuid4()}{extension}"
        absolute_path = self._uploads_root() / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(file_bytes)

        photo = WorkOrderPhoto(
            tenant_id=tenant_id,
            work_order_id=wo_id,
            storage_key=relative_path.as_posix(),
            caption=caption,
            uploaded_by=uploaded_by,
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def list_photos(self, tenant_id: UUID, wo_id: UUID) -> List[WorkOrderPhoto]:
        self.get_wo(tenant_id, wo_id)  # valida existencia + tenant
        stmt = (
            select(WorkOrderPhoto)
            .where(WorkOrderPhoto.work_order_id == wo_id, WorkOrderPhoto.tenant_id == tenant_id)
            .order_by(WorkOrderPhoto.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_photo(self, tenant_id: UUID, wo_id: UUID, photo_id: UUID) -> WorkOrderPhoto:
        photo = self.db.get(WorkOrderPhoto, photo_id)
        if photo is None or photo.tenant_id != tenant_id or photo.work_order_id != wo_id:
            raise WorkOrderNotFound(str(photo_id))
        return photo

    def get_photo_file_path(self, tenant_id: UUID, wo_id: UUID, photo_id: UUID) -> Path:
        photo = self.get_photo(tenant_id, wo_id, photo_id)
        return self._uploads_root() / photo.storage_key

    def delete_photo(self, tenant_id: UUID, wo_id: UUID, photo_id: UUID) -> None:
        wo = self.get_wo(tenant_id, wo_id)
        if wo.status.is_terminal:
            raise TerminalWorkOrder(wo.status.code)

        photo = self.get_photo(tenant_id, wo_id, photo_id)
        absolute_path = self._uploads_root() / photo.storage_key
        self.db.delete(photo)
        self.db.commit()
        absolute_path.unlink(missing_ok=True)
