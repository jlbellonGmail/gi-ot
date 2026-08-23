from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.config_template import DEFAULT_TEMPLATE_CODE, ConfigTemplate
from app.models.role import PLATFORM_OWNER, Role
from app.models.template_asset_type import TemplateAssetType
from app.models.template_priority import TemplatePriority
from app.models.template_work_order_status import TemplateWorkOrderStatus
from app.models.template_work_order_type import TemplateWorkOrderType
from app.models.user import User

# Contenido de la plantilla DEFAULT — debe coincidir con la semilla de datos
# de la migración `config_templates` para que tests y esquema real no diverjan.
DEFAULT_TEMPLATE_PRIORITIES = [
    ("LOW", "Baja", 1),
    ("NORMAL", "Normal", 2),
    ("HIGH", "Alta", 3),
    ("URGENT", "Urgente", 4),
]
DEFAULT_TEMPLATE_WORK_ORDER_TYPES = [
    ("CORRECTIVE", "Correctivo"),
    ("PREVENTIVE", "Preventivo"),
    ("INSTALLATION", "Instalación"),
    ("REVIEW", "Revisión"),
    ("INSPECTION", "Inspección"),
    ("WARRANTY", "Garantía"),
]
DEFAULT_TEMPLATE_WORK_ORDER_STATUSES = [
    ("PENDING", "Pendiente", False),
    ("IN_PROGRESS", "En proceso", False),
    ("COMPLETED", "Terminada", True),
    ("UNRESOLVED", "No resuelta", True),
]
DEFAULT_TEMPLATE_ASSET_TYPES = [
    ("EQUIPMENT", "Equipo"),
    ("INSTALLATION", "Instalación"),
    ("OTHER", "Otro"),
]


def seed_default_config_template(db: Session) -> ConfigTemplate:
    """Crea la plantilla DEFAULT y su contenido estándar, replicando la
    semilla de datos de la migración correspondiente. Uso exclusivo de
    tests (la base real la recibe vía Alembic)."""
    template = ConfigTemplate(code=DEFAULT_TEMPLATE_CODE, name="Configuración estándar")
    db.add(template)
    db.flush()

    for code, label, sort_order in DEFAULT_TEMPLATE_PRIORITIES:
        db.add(TemplatePriority(template_id=template.id, code=code, label=label, sort_order=sort_order))
    for code, label in DEFAULT_TEMPLATE_WORK_ORDER_TYPES:
        db.add(TemplateWorkOrderType(template_id=template.id, code=code, label=label))
    for code, label, is_terminal in DEFAULT_TEMPLATE_WORK_ORDER_STATUSES:
        db.add(
            TemplateWorkOrderStatus(template_id=template.id, code=code, label=label, is_terminal=is_terminal)
        )
    for code, label in DEFAULT_TEMPLATE_ASSET_TYPES:
        db.add(TemplateAssetType(template_id=template.id, code=code, label=label))

    return template


def create_platform_owner(db: Session, email: str = "owner@gi-ot.com", password: str = "Owner123!") -> User:
    role = db.scalar(select(Role).where(Role.code == PLATFORM_OWNER))
    user = User(
        tenant_id=None,
        role_id=role.id,
        email=email,
        full_name="Owner Plataforma",
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_tenant_via_api(client, owner_token: str, name: str, admin_email: str, admin_password: str) -> dict:
    response = client.post(
        "/api/v1/tenants",
        headers=auth_headers(owner_token),
        json={
            "name": name,
            "commercial_name": name,
            "admin_email": admin_email,
            "admin_full_name": f"Admin {name}",
            "admin_password": admin_password,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
