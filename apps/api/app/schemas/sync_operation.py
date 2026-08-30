"""Schemas Pydantic para SyncOperation (ROADMAP §08)."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SyncOperationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operation_type: str
    entity_id: Optional[uuid.UUID] = None
    payload: str
    status: str
    attempt: int
    max_attempts: int
    created_at: datetime
    synced_at: Optional[datetime] = None


class SyncOperationCreate(BaseModel):
    operation_type: str = Field(..., description="Tipo de operación: create_wo, update_wo, register_work, finish_wo, add_photo, reopen_wo, etc.")
    entity_id: Optional[uuid.UUID] = Field(default=None, description="ID de la entidad afectada (p. ej. work_order_id)")
    payload: str = Field(..., description="Payload serializado con los datos de la operación")


class SyncOperationBatch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations: List[SyncOperationCreate] = Field(..., description="Lista de operaciones pendientes a sincronizar")