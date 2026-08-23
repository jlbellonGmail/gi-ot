import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    name: str
    commercial_name: str | None = None
    admin_email: EmailStr
    admin_full_name: str
    admin_password: str


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    commercial_name: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantStatusUpdate(BaseModel):
    status: str


class TenantConfigOut(BaseModel):
    tenant_id: uuid.UUID
    commercial_display_name: str | None
    contact_info: str | None
    receipt_info: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenantConfigUpdate(BaseModel):
    commercial_display_name: str | None = None
    contact_info: str | None = None
    receipt_info: str | None = None
