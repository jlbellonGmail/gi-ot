"""Servicio de comprobantes y comunicaciones (ROADMAP §09).

Genera comprobantes de OT en HTML/PDF, gestiona branding por tenant,
y envía emails (WhatsApp se evalúa aparte).
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.tenant import Tenant, TenantConfig
from app.models.work_order import WorkOrder
from app.models.work_order_receipt import WorkOrderReceipt
from app.schemas.work_order_receipt import TenantBranding, WorkOrderReceiptGenerate, WorkOrderReceiptSend

logger = logging.getLogger(__name__)


class ReceiptService:
    """Servicio para generar y gestionar comprobantes de OT."""

    def __init__(self, db: Session):
        self.db = db

    def _get_template_env(self) -> Environment:
        """Configura Jinja2 para templates."""
        template_dir = Path(__file__).resolve().parent.parent.parent / "templates"
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def get_branding(self, tenant_id: uuid.UUID) -> TenantBranding:
        """Obtiene el branding del tenant desde TenantConfig (método público)."""
        return self._get_branding(tenant_id)

    def _get_branding(self, tenant_id: uuid.UUID) -> TenantBranding:
        """Obtiene el branding del tenant desde TenantConfig."""
        config = self.db.query(TenantConfig).filter_by(tenant_id=tenant_id).first()
        if config:
            return TenantBranding(
                company_name=config.tenant.name if config.tenant else "Empresa",
                logo_url=config.logo_url,
                primary_color=config.primary_color or "#0f172a",
                secondary_color=config.secondary_color or "#1e293b",
                address=config.address,
                phone=config.phone,
                email=config.email,
                website=config.website,
                tax_id=config.tax_id,
            )

        tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
        return TenantBranding(
            company_name=tenant.name if tenant else "Empresa",
            primary_color="#0f172a",
            secondary_color="#1e293b",
        )

    def update_branding(self, tenant_id: uuid.UUID, branding: TenantBranding) -> None:
        """Actualiza el branding del tenant en TenantConfig."""
        config = self.db.query(TenantConfig).filter_by(tenant_id=tenant_id).first()
        if not config:
            config = TenantConfig(tenant_id=tenant_id)
            self.db.add(config)

        config.logo_url = branding.logo_url
        config.primary_color = branding.primary_color
        config.secondary_color = branding.secondary_color
        config.address = branding.address
        config.phone = branding.phone
        config.email = branding.email
        config.website = branding.website
        config.tax_id = branding.tax_id
        config.updated_at = datetime.now(timezone.utc)

        self.db.commit()

    def _render_receipt_html(self, wo: WorkOrder, branding: TenantBranding) -> str:
        """Renderiza el HTML del comprobante usando Jinja2."""
        env = self._get_template_env()
        try:
            template = env.get_template("receipt.html")
        except Exception:
            template = env.from_string(RECEIPT_TEMPLATE_HTML)

        context = {
            "branding": branding.model_dump(),
            "wo": wo,
            "now": datetime.now(timezone.utc),
        }
        return template.render(**context)

    def generate_receipt(
        self,
        tenant_id: uuid.UUID,
        payload: WorkOrderReceiptGenerate,
        generated_by: uuid.UUID,
    ) -> WorkOrderReceipt:
        """Genera el comprobante HTML/PDF para una OT finalizada."""
        wo = self.db.query(WorkOrder).filter_by(
            id=payload.work_order_id, tenant_id=tenant_id
        ).first()
        if not wo:
            raise ValueError("OT no encontrada")

        if not wo.status.is_terminal:
            raise ValueError("Solo se pueden generar comprobantes de OT en estado terminal")

        existing = self.db.query(WorkOrderReceipt).filter_by(
            work_order_id=payload.work_order_id, tenant_id=tenant_id
        ).first()
        if existing and not payload.force_regenerate:
            return existing

        branding = self._get_branding(tenant_id)
        html_content = self._render_receipt_html(wo, branding)
        pdf_key = self._generate_pdf(wo, branding, tenant_id)

        if existing:
            existing.content_html = html_content
            existing.pdf_storage_key = pdf_key
            existing.generated_by = generated_by
            existing.generated_at = datetime.now(timezone.utc)
            receipt = existing
        else:
            receipt = WorkOrderReceipt(
                tenant_id=tenant_id,
                work_order_id=wo.id,
                content_html=html_content,
                pdf_storage_key=pdf_key,
                generated_by=generated_by,
            )
            self.db.add(receipt)

        self.db.commit()
        self.db.refresh(receipt)
        return receipt

    def _generate_pdf(self, wo: WorkOrder, branding: TenantBranding, tenant_id: uuid.UUID) -> str | None:
        """Genera PDF y guarda en storage."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)

            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, branding.company_name or "Comprobante de OT", ln=True, align="C")
            pdf.ln(5)

            pdf.set_font("Helvetica", size=10)
            pdf.cell(0, 6, f"OT N: {wo.number}", ln=True)
            pdf.cell(0, 6, f"Fecha: {wo.finished_at or wo.updated_at}", ln=True)
            pdf.cell(0, 6, f"Estado: {wo.status.label if wo.status else 'N/A'}", ln=True)
            pdf.ln(3)

            if wo.customer and wo.customer.person:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Cliente:", ln=True)
                pdf.set_font("Helvetica", size=10)
                pdf.cell(0, 6, wo.customer.person.display_name or "N/A", ln=True)
            pdf.ln(3)

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Trabajo solicitado:", ln=True)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, wo.requested_description or "N/A")
            pdf.ln(3)

            if wo.performed_description:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Trabajo realizado:", ln=True)
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(0, 5, wo.performed_description)
                pdf.ln(3)

            if wo.technician and wo.technician.person:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Tecnico:", ln=True)
                pdf.set_font("Helvetica", size=10)
                pdf.cell(0, 6, wo.technician.person.display_name or "N/A", ln=True)
            pdf.ln(10)

            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 5, f"Generado el {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}", align="C")

            settings = get_settings()
            uploads_dir = Path(settings.uploads_dir) / "receipts" / str(tenant_id)
            uploads_dir.mkdir(parents=True, exist_ok=True)
            filename = f"receipt_{wo.id}_{uuid.uuid4().hex[:8]}.pdf"
            filepath = uploads_dir / filename
            pdf.output(str(filepath))

            return f"receipts/{tenant_id}/{filename}"
        except Exception as e:
            logger.error(f"Error generating PDF for work_order {wo.id}: {e}")
            return None

    def send_receipt_email(
        self,
        tenant_id: uuid.UUID,
        payload: WorkOrderReceiptSend,
        sent_by: uuid.UUID,
    ) -> bool:
        """Envía el comprobante por email."""
        receipt = self.db.query(WorkOrderReceipt).filter_by(
            work_order_id=payload.work_order_id, tenant_id=tenant_id
        ).first()
        if not receipt:
            raise ValueError("Comprobante no encontrado")

        # Obtener configuración de email
        settings = get_settings()
        smtp_host = getattr(settings, "smtp_host", None)
        smtp_port = getattr(settings, "smtp_port", 587)
        smtp_user = getattr(settings, "smtp_user", None)
        smtp_password = getattr(settings, "smtp_password", None)
        smtp_from = getattr(settings, "smtp_from", None)
        smtp_use_tls = getattr(settings, "smtp_use_tls", True)

        subject = payload.subject or f"Comprobante OT #{receipt.work_order_id}"
        body = payload.body or f"Adjunto encontrará el comprobante de la OT."

        # Si no hay configuración SMTP, registrar como pendiente y retornar éxito condicional
        if not smtp_host or not smtp_user or not smtp_from:
            logger.warning(
                f"Email no enviado para receipt {receipt.id}: configuración SMTP incompleta. "
                f"Marcando como pendiente de envío."
            )
            # No marcar como enviado si no hay configuración real
            return False

        # Enviar email real via SMTP
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.application import MIMEApplication

            msg = MIMEMultipart()
            msg["From"] = smtp_from
            msg["To"] = payload.recipient_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            # Adjuntar PDF si existe
            if receipt.pdf_storage_key:
                pdf_path = Path(settings.uploads_dir) / receipt.pdf_storage_key
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
                        pdf_attachment.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=f"comprobante_ot_{receipt.work_order_id}.pdf",
                        )
                        msg.attach(pdf_attachment)

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info(f"Email enviado exitosamente para receipt {receipt.id} a {payload.recipient_email}")

        except Exception as e:
            logger.error(f"Error enviando email para receipt {receipt.id}: {e}")
            raise ValueError(f"Error al enviar email: {str(e)}")

        # Solo marcar como enviado después de confirmación válida
        receipt.sent_to_email = True
        receipt.last_sent_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def send_receipt_whatsapp(
        self,
        tenant_id: uuid.UUID,
        work_order_id: uuid.UUID,
        phone: str,
    ) -> bool:
        """Envía el comprobante por WhatsApp.

        NOTA: Según ROADMAP §09, WhatsApp debe evaluarse según decisión técnica y comercial.
        No bloquea el MVP. Esta implementación es un placeholder que registra la intención
        y devuelve False indicando que no se envió realmente.

        Cuando se tome la decisión técnica (proveedor: Twilio, Meta Cloud API, etc.),
        esta función debe implementarse completamente.
        """
        receipt = self.db.query(WorkOrderReceipt).filter_by(
            work_order_id=work_order_id, tenant_id=tenant_id
        ).first()
        if not receipt:
            raise ValueError("Comprobante no encontrado")

        logger.info(
            f"WhatsApp send requested for receipt {receipt.id} to {phone}. "
            f"Funcionalidad pendiente de decisión técnica/comercial (ROADMAP §09)."
        )

        # No marcar como enviado - solo registrar la solicitud
        # Cuando se implemente realmente, aquí iría la llamada al proveedor (Twilio, Meta, etc.)
        # y se marcaría receipt.sent_to_whatsapp = True tras confirmación
        return False


RECEIPT_TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Helvetica, Arial, sans-serif; margin: 20px; color: #1e293b; }
        .header { text-align: center; border-bottom: 2px solid {{ branding.primary_color }}; padding-bottom: 10px; margin-bottom: 20px; }
        .company-name { color: {{ branding.primary_color }}; font-size: 24px; font-weight: bold; margin: 0; }
        .section { margin-bottom: 20px; }
        .section-title { color: {{ branding.primary_color }}; font-weight: bold; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
        .detail-row { display: flex; margin: 8px 0; }
        .detail-label { font-weight: bold; width: 150px; flex-shrink: 0; }
        .detail-value { flex: 1; }
        .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #64748b; }
        .description { white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="company-name">{{ branding.company_name }}</h1>
    </div>

    <div class="section">
        <div class="section-title">COMPROBANTE DE ORDEN DE TRABAJO</div>
        <div class="detail-row"><span class="detail-label">OT N:</span><span class="detail-value">{{ wo.number }}</span></div>
        <div class="detail-row"><span class="detail-label">Fecha:</span><span class="detail-value">{{ (wo.finished_at or wo.updated_at).strftime('%d/%m/%Y %H:%M') if wo.finished_at or wo.updated_at else 'N/A' }}</span></div>
        <div class="detail-row"><span class="detail-label">Estado:</span><span class="detail-value">{{ wo.status.label if wo.status else 'N/A' }}</span></div>
    </div>

    <div class="section">
        <div class="section-title">CLIENTE</div>
        {% if wo.customer and wo.customer.person %}
        <div class="detail-row"><span class="detail-label">Nombre:</span><span class="detail-value">{{ wo.customer.person.display_name }}</span></div>
        <div class="detail-row"><span class="detail-label">Telefono:</span><span class="detail-value">{{ wo.customer.person.phone or 'N/A' }}</span></div>
        <div class="detail-row"><span class="detail-label">Email:</span><span class="detail-value">{{ wo.customer.person.email or 'N/A' }}</span></div>
        {% endif %}
    </div>

    <div class="section">
        <div class="section-title">UBICACION / ACTIVO</div>
        {% if wo.location %}<div class="detail-row"><span class="detail-label">Ubicacion:</span><span class="detail-value">{{ wo.location.name }}</span></div>{% endif %}
        {% if wo.asset %}<div class="detail-row"><span class="detail-label">Activo:</span><span class="detail-value">{{ wo.asset.name }}</span></div>{% endif %}
    </div>

    <div class="section">
        <div class="section-title">TRABAJO SOLICITADO</div>
        <div class="description">{{ wo.requested_description }}</div>
    </div>

    {% if wo.performed_description %}
    <div class="section">
        <div class="section-title">TRABAJO REALIZADO</div>
        <div class="description">{{ wo.performed_description }}</div>
    </div>
    {% endif %}

    {% if wo.technician and wo.technician.person %}
    <div class="section">
        <div class="section-title">TECNICO RESPONSABLE</div>
        <div class="detail-row"><span class="detail-label">Nombre:</span><span class="detail-value">{{ wo.technician.person.display_name }}</span></div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Generado el {{ now.strftime('%d/%m/%Y %H:%M') }} | {{ branding.company_name }}</p>
    </div>
</body>
</html>
"""