import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.rls import set_platform_context
from app.db.session import get_db
from app.main import app
from app.models.role import ALL_ROLE_CODES, Role
from app.models.tenant import Tenant, TenantConfig
from app.models.user import User
from app.models.person import Person, Customer, Technician
from app.models.location import Location, Asset
from app.models.asset_type import AssetType
from app.models.work_order import WorkOrder, WorkOrderHistory, WorkOrderPhoto
from app.models.work_order_type import WorkOrderType
from app.models.work_order_status import WorkOrderStatus
from app.models.priority import Priority
from app.models.work_order_receipt import WorkOrderReceipt
from app.models.sync_operation import SyncOperation

from tests.helpers import seed_default_config_template

_test_database_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
_is_postgresql = _test_database_url.startswith("postgresql")
_engine_kwargs = {}
if _test_database_url.startswith("sqlite"):
    _engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

engine = create_engine(_test_database_url, **_engine_kwargs)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _fresh_schema():
    if _is_postgresql:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    set_platform_context(session)
    default_labels = {
        "PLATFORM_OWNER": "Propietario de la plataforma",
        "TENANT_ADMIN": "Administrador de empresa",
        "TENANT_OFFICE": "Administrativo",
        "TENANT_TECHNICIAN": "Técnico",
    }
    for code in ALL_ROLE_CODES:
        session.add(Role(code=code, default_label=default_labels[code]))
    session.commit()

    seed_default_config_template(session)
    session.commit()
    session.close()
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
