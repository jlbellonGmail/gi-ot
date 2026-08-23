import uuid

from pydantic import BaseModel, Field


class AssetTypeOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    label: str
    active: bool

    model_config = {"from_attributes": True}


class AssetTypeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)


class AssetTypeUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    active: bool | None = None


class WorkOrderTypeOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    label: str
    active: bool

    model_config = {"from_attributes": True}


class WorkOrderTypeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)


class WorkOrderTypeUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    active: bool | None = None


class PriorityOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    label: str
    sort_order: int
    active: bool

    model_config = {"from_attributes": True}


class PriorityCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=100)
    sort_order: int = 0


class PriorityUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    sort_order: int | None = None
    active: bool | None = None


class WorkOrderStatusOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    label: str
    is_terminal: bool
    active: bool

    model_config = {"from_attributes": True}


class WorkOrderStatusUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    active: bool | None = None
