from enum import Enum


class WorkOrderStatusCode(str, Enum):
    """Códigos de estado fijos de OT (modelo-datos.md §4.13)."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    UNRESOLVED = "UNRESOLVED"


class HistoryEventType(str, Enum):
    """Tipos de evento para el historial de auditoría de OT."""
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    STATUS_CHANGE = "STATUS_CHANGE"
    REOPENED = "REOPENED"