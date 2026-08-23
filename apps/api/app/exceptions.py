"""Excepciones personalizadas para la aplicación GI-OT."""

class InvalidTransition(Exception):
    """Transición de estado no permitida en la máquina de estados de OT."""
    def __init__(self, current_code: str, target_code: str):
        self.current_code = current_code
        self.target_code = target_code
        super().__init__(f"Transición inválida: '{current_code}' → '{target_code}'")


class TerminalWorkOrder(Exception):
    """Intento de operación sobre una OT en estado terminal."""
    def __init__(self, current_code: str):
        self.current_code = current_code
        super().__init__(f"OT en estado terminal '{current_code}'; operaciones prohibidas hasta reabrir")


class RefValidationError(Exception):
    """Referencia externa (FK) que no pertenece al tenant de contexto."""
    def __init__(self, ref_name: str):
        self.ref_name = ref_name
        super().__init__(f"La referencia '{ref_name}' no pertenece al tenant actual")


class WorkOrderNotFound(Exception):
    """OT no encontrada o acceso no autorizado."""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"OT con identificador '{identifier}' no encontrada o acceso denegado")


class TechnicianNotFound(Exception):
    """Técnico no encontrado en el tenant."""
    def __init__(self, technician_id: str):
        self.technician_id = technician_id
        super().__init__(f"Técnico con ID '{technician_id}' no encontrado en el tenant")


class TechnicianUserLinkError(Exception):
    """El User a vincular con un Technician no es válido: no existe, no
    pertenece al tenant, no tiene rol TENANT_TECHNICIAN, o ya está
    vinculado a otro Technician del tenant."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class TechnicianNotLinked(Exception):
    """El usuario técnico autenticado no tiene un Technician vinculado
    (requerido para crear una OT urgente desde el campo — PRD §20)."""
    pass