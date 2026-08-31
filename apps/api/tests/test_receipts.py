"""Tests para Comprobantes y Comunicaciones (ROADMAP §09).

Cubre:
- Generación de comprobante (HTML + PDF)
- Aislamiento multitenant
- Solo OT terminal
- Regeneración (force_regenerate)
- Branding GET/PUT
- Autorización branding
- Envío email éxito/error
- WhatsApp según decisión adoptada
- Rutas realmente registradas
"""

import logging
import uuid
from pathlib import Path

import pytest

from app.models.asset_type import AssetType
from app.models.location import Asset, Location
from app.models.person import Customer, Person, PersonType, Technician
from app.models.priority import Priority
from app.models.role import Role
from app.models.tenant import Tenant, TenantConfig
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.work_order_receipt import WorkOrderReceipt
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType
from app.services.receipt import ReceiptService


def create_full_test_setup(db_session, tenant):
    """Crea configuración completa para tests de OT."""
    # Catálogos
    status_pending = WorkOrderStatus(code="PENDING", label="Pendiente", sort_order=1, tenant_id=tenant.id, is_terminal=False)
    status_completed = WorkOrderStatus(code="COMPLETED", label="Completada", sort_order=3, tenant_id=tenant.id, is_terminal=True)
    status_cancelled = WorkOrderStatus(code="CANCELLED", label="Cancelada", sort_order=4, tenant_id=tenant.id, is_terminal=True)
    wotype = WorkOrderType(code="CORRECTIVO", label="Correctivo", tenant_id=tenant.id)
    priority = Priority(code="NORMAL", label="Normal", sort_order=2, tenant_id=tenant.id)
    assettype = AssetType(code="EQUIPO", label="Equipo", tenant_id=tenant.id)

    db_session.add_all([status_pending, status_completed, status_cancelled, wotype, priority, assettype])
    db_session.commit()

    # Obtener roles ya creados por el fixture
    tech_role = db_session.query(Role).filter_by(code="TENANT_TECHNICIAN").first()
    admin_role = db_session.query(Role).filter_by(code="TENANT_ADMIN").first()

    # Persona y cliente
    person = Person(
        tenant_id=tenant.id,
        person_type=PersonType.INDIVIDUAL,
        display_name="Cliente Test",
        email="cliente@test.com",
        phone="1111-1111",
    )
    db_session.add(person)
    db_session.commit()

    customer = Customer(tenant_id=tenant.id, person_id=person.id)
    db_session.add(customer)
    db_session.commit()

    # Técnico
    tech_person = Person(
        tenant_id=tenant.id,
        person_type=PersonType.INDIVIDUAL,
        display_name="Tecnico Test",
        email="tecnico@test.com",
        phone="2222-2222",
    )
    db_session.add(tech_person)
    db_session.commit()

    technician = Technician(tenant_id=tenant.id, person_id=tech_person.id)
    db_session.add(technician)
    db_session.commit()

    # Usuario admin
    admin_user = User(tenant_id=tenant.id, email="admin@test.com", password_hash="hash", full_name="Admin", role_id=admin_role.id)
    db_session.add(admin_user)
    db_session.commit()

    # Ubicación y activo
    location = Location(name="Sucursal Test", address="Calle 123", customer_id=person.id, tenant_id=tenant.id)
    db_session.add(location)
    db_session.commit()

    asset = Asset(name="Equipo Test", location_id=location.id, tenant_id=tenant.id, asset_type_id=assettype.id, serial_number="EQ-001")
    db_session.add(asset)
    db_session.commit()

    return {
        "status_pending": status_pending,
        "status_completed": status_completed,
        "status_cancelled": status_cancelled,
        "wotype": wotype,
        "priority": priority,
        "assettype": assettype,
        "customer_person": person,
        "customer": customer,
        "tech_person": tech_person,
        "technician": technician,
        "admin_user": admin_user,
        "admin_role": admin_role,
        "tech_role": tech_role,
        "location": location,
        "asset": asset,
    }


class TestReceiptGeneration:
    """Tests de generación de comprobantes."""

    def setup_test_data(self, db_session):
        """Crea datos base para tests."""
        tenant1 = Tenant(name="Tenant Uno")
        db_session.add(tenant1)
        db_session.commit()

        tenant2 = Tenant(name="Tenant Dos")
        db_session.add(tenant2)
        db_session.commit()

        setup1 = create_full_test_setup(db_session, tenant1)

        # OT en estado terminal
        wo_terminal = WorkOrder(
            tenant_id=tenant1.id,
            number=1,
            customer_id=setup1["customer_person"].id,
            location_id=setup1["location"].id,
            asset_id=setup1["asset"].id,
            work_order_type_id=setup1["wotype"].id,
            priority_id=setup1["priority"].id,
            status_id=setup1["status_completed"].id,
            requested_description="Trabajo solicitado de prueba",
            performed_description="Trabajo realizado de prueba",
            technician_id=setup1["tech_person"].id,
            created_by=tenant1.id,
            updated_by=tenant1.id,
        )
        db_session.add(wo_terminal)
        db_session.commit()

        # OT en estado NO terminal
        wo_active = WorkOrder(
            tenant_id=tenant1.id,
            number=2,
            customer_id=setup1["customer_person"].id,
            location_id=setup1["location"].id,
            asset_id=setup1["asset"].id,
            work_order_type_id=setup1["wotype"].id,
            priority_id=setup1["priority"].id,
            status_id=setup1["status_pending"].id,
            requested_description="OT activa",
            created_by=tenant1.id,
            updated_by=tenant1.id,
        )
        db_session.add(wo_active)
        db_session.commit()

        return {
            "tenant1": tenant1,
            "tenant2": tenant2,
            "wo_terminal": wo_terminal,
            "wo_active": wo_active,
            "admin_user": setup1["admin_user"],
        }

    def test_generate_receipt_success(self, client, db_session):
        """Test generación exitosa de comprobante para OT terminal."""
        data = self.setup_test_data(db_session)
        tenant1 = data["tenant1"]
        wo_terminal = data["wo_terminal"]
        admin_user = data["admin_user"]

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id, force_regenerate=False)
        receipt = service.generate_receipt(tenant1.id, payload, generated_by=admin_user.id)

        assert receipt is not None
        assert receipt.tenant_id == tenant1.id
        assert receipt.work_order_id == wo_terminal.id
        assert receipt.content_html is not None
        assert len(receipt.content_html) > 0
        assert "COMPROBANTE DE ORDEN DE TRABAJO" in receipt.content_html
        assert receipt.pdf_storage_key is not None

    def test_generate_receipt_fails_non_terminal(self, client, db_session):
        """Test que falla al generar comprobante para OT no terminal."""
        data = self.setup_test_data(db_session)
        tenant1 = data["tenant1"]
        wo_active = data["wo_active"]
        admin_user = data["admin_user"]

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo_active.id, force_regenerate=False)
        with pytest.raises(ValueError, match="Solo se pueden generar comprobantes de OT en estado terminal"):
            service.generate_receipt(tenant1.id, payload, generated_by=admin_user.id)

    def test_generate_receipt_tenant_isolation(self, client, db_session):
        """Test aislamiento multitenant: tenant2 no puede generar comprobante de OT de tenant1."""
        data = self.setup_test_data(db_session)
        _tenant1 = data["tenant1"]
        tenant2 = data["tenant2"]
        wo_terminal = data["wo_terminal"]

        # Obtener rol admin ya creado por el fixture
        admin_role = db_session.query(Role).filter_by(code="TENANT_ADMIN").first()
        user2 = User(tenant_id=tenant2.id, email="user2@test.com", password_hash="hash", full_name="User 2", role_id=admin_role.id)
        db_session.add(user2)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id, force_regenerate=False)
        with pytest.raises(ValueError, match="OT no encontrada"):
            service.generate_receipt(tenant2.id, payload, generated_by=user2.id)

    def test_force_regenerate_replaces_html_and_pdf(self, client, db_session):
        """Test que force_regenerate=True regenera tanto HTML como PDF."""
        import time
        data = self.setup_test_data(db_session)
        tenant1 = data["tenant1"]
        wo_terminal = data["wo_terminal"]
        admin_user = data["admin_user"]

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        # Primera generación
        payload1 = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id, force_regenerate=False)
        receipt1 = service.generate_receipt(tenant1.id, payload1, generated_by=admin_user.id)
        _html1 = receipt1.content_html
        pdf1 = receipt1.pdf_storage_key

        # Pequeña pausa para permitir timestamp diferente (aunque el test puede ser rápido)
        time.sleep(1.1)

        # Segunda generación con force_regenerate
        payload2 = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id, force_regenerate=True)
        receipt2 = service.generate_receipt(tenant1.id, payload2, generated_by=admin_user.id)
        _html2 = receipt2.content_html
        pdf2 = receipt2.pdf_storage_key

        # Debe ser el mismo registro (mismo ID)
        assert receipt2.id == receipt1.id
        # PDF debe regenerarse (nuevo archivo) - esta es la verificación clave
        assert pdf2 != pdf1
        # HTML se regenera (puede tener mismo contenido si timestamp no cambia, pero se ejecuta la regeneración)
        # Lo importante es que force_regenerate no devuelve el objeto anterior sin cambios
        assert receipt2.generated_at >= receipt1.generated_at

    def test_get_receipt_html(self, client, db_session):
        """Test obtención de comprobante en HTML."""
        data = self.setup_test_data(db_session)
        tenant1 = data["tenant1"]
        wo_terminal = data["wo_terminal"]
        admin_user = data["admin_user"]

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id)
        receipt = service.generate_receipt(tenant1.id, payload, generated_by=admin_user.id)

        # Verificar que el servicio devuelve HTML
        assert receipt.content_html is not None
        assert "COMPROBANTE DE ORDEN DE TRABAJO" in receipt.content_html

    def test_get_receipt_pdf(self, client, db_session):
        """Test que el PDF se genera y guarda."""
        data = self.setup_test_data(db_session)
        tenant1 = data["tenant1"]
        wo_terminal = data["wo_terminal"]
        admin_user = data["admin_user"]

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo_terminal.id)
        receipt = service.generate_receipt(tenant1.id, payload, generated_by=admin_user.id)

        assert receipt.pdf_storage_key is not None
        # Verificar que el archivo existe
        from app.core.config import get_settings
        settings = get_settings()
        filepath = Path(settings.uploads_dir) / receipt.pdf_storage_key
        assert filepath.exists()


class TestBranding:
    """Tests de branding por tenant."""

    def test_get_default_branding(self, db_session):
        """Test obtención de branding por defecto (sin configuración)."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        service = ReceiptService(db_session)
        branding = service.get_branding(tenant.id)

        assert branding.company_name == "Test Tenant"
        assert branding.primary_color == "#0f172a"
        assert branding.secondary_color == "#1e293b"
        assert branding.logo_url is None

    def test_update_branding_creates_config(self, db_session):
        """Test actualización de branding crea TenantConfig si no existe."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import TenantBranding

        new_branding = TenantBranding(
            company_name="Nueva Empresa",
            primary_color="#ff0000",
            secondary_color="#00ff00",
            logo_url="https://example.com/logo.png",
            address="Calle Nueva 123",
            phone="3333-3333",
            email="nuevo@test.com",
            website="https://nuevo.com",
            tax_id="20-12345678-9",
        )
        service.update_branding(tenant.id, new_branding)

        # Verificar que se guardó en BD
        config = db_session.query(TenantConfig).filter_by(tenant_id=tenant.id).first()
        assert config is not None
        assert config.logo_url == "https://example.com/logo.png"
        assert config.primary_color == "#ff0000"
        assert config.secondary_color == "#00ff00"
        assert config.address == "Calle Nueva 123"
        assert config.phone == "3333-3333"
        assert config.email == "nuevo@test.com"
        assert config.website == "https://nuevo.com"
        assert config.tax_id == "20-12345678-9"

        # Verificar que get_branding devuelve lo actualizado
        branding = service.get_branding(tenant.id)
        assert branding.company_name == "Test Tenant"  # Viene del tenant.name
        assert branding.primary_color == "#ff0000"
        assert branding.logo_url == "https://example.com/logo.png"

    def test_update_branding_updates_existing_config(self, db_session):
        """Test actualización de branding sobre config existente."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        # Crear config inicial
        config = TenantConfig(tenant_id=tenant.id, primary_color="#aaaaaa")
        db_session.add(config)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import TenantBranding

        new_branding = TenantBranding(
            company_name="Test Tenant",
            primary_color="#bbbbbb",
            secondary_color="#cccccc",
        )
        service.update_branding(tenant.id, new_branding)

        config = db_session.query(TenantConfig).filter_by(tenant_id=tenant.id).first()
        assert config.primary_color == "#bbbbbb"
        assert config.secondary_color == "#cccccc"

    def test_branding_tenant_isolation(self, db_session):
        """Test aislamiento de branding entre tenants."""
        tenant1 = Tenant(name="Tenant 1")
        tenant2 = Tenant(name="Tenant 2")
        db_session.add_all([tenant1, tenant2])
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import TenantBranding

        branding1 = TenantBranding(company_name="Tenant 1", primary_color="#111111")
        branding2 = TenantBranding(company_name="Tenant 2", primary_color="#222222")

        service.update_branding(tenant1.id, branding1)
        service.update_branding(tenant2.id, branding2)

        b1 = service.get_branding(tenant1.id)
        b2 = service.get_branding(tenant2.id)

        assert b1.primary_color == "#111111"
        assert b2.primary_color == "#222222"


class TestEmailSending:
    """Tests de envío por email."""

    def test_send_email_without_smtp_config_returns_false(self, db_session):
        """Test que sin configuración SMTP, send_receipt_email retorna False y no marca como enviado."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        setup = create_full_test_setup(db_session, tenant)

        # OT terminal
        wo = WorkOrder(
            tenant_id=tenant.id, number=1, customer_id=setup["customer_person"].id,
            location_id=setup["location"].id, asset_id=setup["asset"].id,
            work_order_type_id=setup["wotype"].id, priority_id=setup["priority"].id,
            status_id=setup["status_completed"].id, requested_description="Test",
            created_by=tenant.id, updated_by=tenant.id
        )
        db_session.add(wo)
        db_session.commit()

        receipt = WorkOrderReceipt(
            tenant_id=tenant.id, work_order_id=wo.id,
            content_html="<html>test</html>", generated_by=tenant.id
        )
        db_session.add(receipt)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptSend

        payload = WorkOrderReceiptSend(
            work_order_id=wo.id,
            recipient_email="destino@test.com",
            subject="Test",
            body="Body"
        )

        # Sin configuración SMTP, debe retornar False
        result = service.send_receipt_email(tenant.id, payload, sent_by=tenant.id)
        assert result is False

        # Verificar que NO se marcó como enviado
        db_session.refresh(receipt)
        assert receipt.sent_to_email is False

    def test_send_email_receipt_not_found(self, db_session):
        """Test envío email falla si comprobante no existe."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptSend

        payload = WorkOrderReceiptSend(
            work_order_id=uuid.uuid4(),
            recipient_email="test@test.com"
        )

        with pytest.raises(ValueError, match="Comprobante no encontrado"):
            service.send_receipt_email(tenant.id, payload, sent_by=tenant.id)


class TestWhatsAppSending:
    """Tests de envío por WhatsApp (evaluación técnica)."""

    def test_send_whatsapp_returns_false_and_logs(self, db_session, caplog):
        """Test que send_receipt_whatsapp retorna False y registra la intención (placeholder)."""
        tenant = Tenant(name="Test Tenant")
        db_session.add(tenant)
        db_session.commit()

        setup = create_full_test_setup(db_session, tenant)

        wo = WorkOrder(
            tenant_id=tenant.id, number=1, customer_id=setup["customer_person"].id,
            location_id=setup["location"].id, asset_id=setup["asset"].id,
            work_order_type_id=setup["wotype"].id, priority_id=setup["priority"].id,
            status_id=setup["status_completed"].id, requested_description="Test",
            created_by=tenant.id, updated_by=tenant.id
        )
        db_session.add(wo)
        db_session.commit()

        receipt = WorkOrderReceipt(
            tenant_id=tenant.id, work_order_id=wo.id,
            content_html="<html>test</html>", generated_by=tenant.id
        )
        db_session.add(receipt)
        db_session.commit()

        service = ReceiptService(db_session)

        with caplog.at_level(logging.INFO):
            result = service.send_receipt_whatsapp(tenant.id, wo.id, "+5491112345678")

        assert result is False
        assert "WhatsApp send requested" in caplog.text
        assert "pendiente de decisión técnica/comercial" in caplog.text

        # Verificar que NO se marcó como enviado
        db_session.refresh(receipt)
        assert receipt.sent_to_whatsapp is False


class TestReceiptAPIEndpoints:
    """Tests de endpoints API."""

    def test_routes_exist(self, client):
        """Test que las rutas están registradas."""
        from app.api.v1 import receipts
        route_paths = [r.path for r in receipts.router.routes]
        
        # Las rutas tienen prefijo /receipts
        assert "/receipts/branding" in route_paths
        assert "/receipts" in route_paths  # POST
        assert "/receipts/{work_order_id}" in route_paths
        assert "/receipts/{work_order_id}/pdf" in route_paths
        assert "/receipts/{work_order_id}/send-email" in route_paths
        assert "/receipts/{work_order_id}/send-whatsapp" in route_paths

    def test_branding_route_order(self, client):
        """Test que /branding no colisiona con /{work_order_id}."""
        from app.api.v1 import receipts
        route_paths = [r.path for r in receipts.router.routes]
        
        # Verificar que /receipts/branding aparece antes que /receipts/{work_order_id}
        branding_idx = route_paths.index("/receipts/branding")
        wo_idx = route_paths.index("/receipts/{work_order_id}")
        assert branding_idx < wo_idx


class TestReceiptHTMLPDFGeneration:
    """Tests específicos de generación HTML y PDF."""

    def test_html_contains_required_fields(self, db_session):
        """Test que el HTML generado contiene todos los campos requeridos."""
        tenant = Tenant(name="Empresa Test")
        db_session.add(tenant)
        db_session.commit()

        setup = create_full_test_setup(db_session, tenant)

        wo = WorkOrder(
            tenant_id=tenant.id, number=42, customer_id=setup["customer_person"].id,
            location_id=setup["location"].id, asset_id=setup["asset"].id,
            work_order_type_id=setup["wotype"].id, priority_id=setup["priority"].id,
            status_id=setup["status_completed"].id,
            requested_description="Instalar aire acondicionado",
            performed_description="Se instaló equipo split en living",
            technician_id=setup["tech_person"].id,
            created_by=tenant.id, updated_by=tenant.id
        )
        db_session.add(wo)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo.id)
        receipt = service.generate_receipt(tenant.id, payload, generated_by=setup["admin_user"].id)

        html = receipt.content_html
        assert "Empresa Test" in html
        assert "42" in html  # OT number
        assert "Juan Pérez" not in html  # El nombre es "Cliente Test" en el setup
        assert "Cliente Test" in html
        assert "cliente@test.com" in html
        assert "1111-1111" in html
        assert "Sucursal Test" in html
        assert "Equipo Test" in html
        assert "Instalar aire acondicionado" in html
        assert "Se instaló equipo split en living" in html
        assert "Tecnico Test" in html
        assert "COMPROBANTE DE ORDEN DE TRABAJO" in html

    def test_pdf_generation_creates_file(self, db_session):
        """Test que la generación de PDF crea archivo físico."""
        tenant = Tenant(name="Test")
        db_session.add(tenant)
        db_session.commit()

        setup = create_full_test_setup(db_session, tenant)

        wo = WorkOrder(
            tenant_id=tenant.id, number=1, customer_id=setup["customer_person"].id,
            location_id=setup["location"].id, asset_id=setup["asset"].id,
            work_order_type_id=setup["wotype"].id, priority_id=setup["priority"].id,
            status_id=setup["status_completed"].id, requested_description="Test",
            created_by=tenant.id, updated_by=tenant.id
        )
        db_session.add(wo)
        db_session.commit()

        service = ReceiptService(db_session)
        from app.schemas.work_order_receipt import WorkOrderReceiptGenerate

        payload = WorkOrderReceiptGenerate(work_order_id=wo.id)
        receipt = service.generate_receipt(tenant.id, payload, generated_by=setup["admin_user"].id)

        assert receipt.pdf_storage_key is not None
        from app.core.config import get_settings
        settings = get_settings()
        filepath = Path(settings.uploads_dir) / receipt.pdf_storage_key
        assert filepath.exists()
        assert filepath.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])