import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role_code: str
    tenant_id: uuid.UUID | None
    # Solo se completa cuando role_code es TENANT_TECHNICIAN y el usuario
    # está vinculado a un Technician (ver Technician.user_id) — habilita
    # "Mis OT" en el flujo mobile (ROADMAP §06).
    technician_person_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}
