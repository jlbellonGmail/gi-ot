"""Endpoints FastAPI para sincronización offline (ROADMAP §08).

Endpoint POST /api/v1/sync — Procesa las SyncOperation pendientes
cuando el dispositivo vuelve a tener conectividad.

El flujo es:
1. Cliente envía las operaciones pendientes en el cuerpo.
2. API valida que pertenecen al tenant autenticado.
3. API aplica cada operación idempotente (crear/actualizar/registrar/fin/etc.).
4. Marca cada operación como `synced` en la base de datos.
5. Responde con el estado de cada operación.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, get_current_user, get_db
from app.models.sync_operation import SyncOperation
from app.models.work_order import WorkOrder
from app.schemas.sync_operation import SyncOperationOut, SyncOperationBatch
from app.services.sync import process_sync_operations


router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=List[SyncOperationOut])
def sync_operations(
    batch: SyncOperationBatch,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> List[SyncOperationOut]:
    """Procesa las operaciones pendientes de sincronización.

    El cuerpo debe contener una lista de SyncOperation con sus IDs y los
    datos actualizados. El backend aplica cada operación y devuelve el
    estado resultante.
    """
    return process_sync_operations(db, tenant_id, batch.operations)