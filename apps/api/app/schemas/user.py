import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role_code: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role_code: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
