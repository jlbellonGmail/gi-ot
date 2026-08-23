"""Schemas Pydantic para el módulo WorkOrder (Etapa 04 — Núcleo de OT)."""

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Códigos de estado con semántica interna fija (modelo-datos.md §4.13).
# El tenant puede renombrar el `label` visible, nunca el `code`.
TERMINAL_STATUS_CODES = ("COMPLETED", "UNRESOLVED")


class WorkOrderCreate(BaseModel):
    customer_id: uuid.UUID
    location_id: uuid.UUID
    asset_id: uuid.UUID
    work_order_type_id: uuid.UUID
    priority_id: uuid.UUID
    requested_description: str = Field(min_length=1)
    technician_id: Optional[uuid.UUID] = None
    scheduled_at: Optional[datetime] = None


class WorkOrderUpdate(BaseModel):
    """Edición de campos de gestión (no de ejecución). Solo permitida
    mientras la OT no haya alcanzado un estado terminal (§4.12)."""
    requested_description: Optional[str] = Field(default=None, min_length=1)
    scheduled_at: Optional[datetime] = None
    work_order_type_id: Optional[uuid.UUID] = None
    priority_id: Optional[uuid.UUID] = None


class WorkOrderRegisterWork(BaseModel):
    """Registro del trabajo realizado por el técnico."""
    performed_description: str = Field(min_length=1)


class WorkOrderAssign(BaseModel):
    technician_id: uuid.UUID


class WorkOrderFinish(BaseModel):
    status_code: Literal["COMPLETED", "UNRESOLVED"]
    performed_description: Optional[str] = None


class WorkOrderReopen(BaseModel):
    """Reapertura controlada: el motivo es obligatorio para preservar
    trazabilidad (PRD §49, modelo-funcional.md §9)."""
    notes: str = Field(min_length=3)


class WorkOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    number: int
    customer_id: uuid.UUID
    location_id: uuid.UUID
    asset_id: uuid.UUID
    technician_id: Optional[uuid.UUID] = None
    work_order_type_id: uuid.UUID
    priority_id: uuid.UUID
    status_id: uuid.UUID
    requested_description: str
    performed_description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    # Semántica interna estable + etiqueta visible configurable (AGENTS.md)
    status_code: Optional[str] = None
    status_label: Optional[str] = None
    is_terminal: bool = False
    priority_code: Optional[str] = None
    priority_label: Optional[str] = None


class WorkOrderHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    work_order_id: uuid.UUID
    event_type: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    performed_by: Optional[uuid.UUID] = None
    performed_at: datetime
    notes: Optional[str] = None


class WorkOrderPhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_order_id: uuid.UUID
    caption: Optional[str] = None
    taken_at: datetime
    uploaded_by: Optional[uuid.UUID] = None
    created_at: datetime