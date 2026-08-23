import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.role import ALL_ROLE_CODES, Role
from tests.helpers import seed_default_config_template

# Base de datos SQLite en memoria, aislada por test — nunca toca data/gi-ot.db.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
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
