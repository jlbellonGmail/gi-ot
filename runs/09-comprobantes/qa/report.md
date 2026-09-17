# QA — 09 Comprobantes y comunicaciones

## Resultado: ✅ APROBADO

## Cobertura de pruebas
- `apps/api/tests/test_receipts.py` — 10 tests (7 API + 3 branding)

## Verificación de criterios de aceptación

### ✅ Comprobante se genera solo para OT en estado terminal
- Validación en `generate_receipt()`: `if not wo.status.is_terminal`
- Estado 400 si no es terminal

### ✅ Branding se aplica del TenantConfig
- `_get_branding()` recoge columnas de TenantConfig
- Valores por defecto: primary_color="#0f172a", secondary_color="#1e293b"

### ✅ PDF se genera y guarda en storage
- `_generate_pdf()` usa FPDF
- Guarda en `uploads/receipts/{tenant_id}/`

### ✅ Email/WhatsApp marcan como enviado (stub)
- `send_receipt_email()` y `send_receipt_whatsapp()` actualizan `sent_to_email`/`sent_to_whatsapp`
- Listo para integrar proveedor real

### ✅ Branding actualizable via API
- `PUT /api/v1/receipts/branding` actualiza TenantConfig

## Multitenancy
- Todo endpoint valida tenant_id server-side
- Branding es por tenant (TenantConfig)
- Sin exposición cruzada de tenants

## Seguridad
- Solo TENANT_ADMIN y TENANT_OFFICE pueden generar comprobantes
- Solo TENANT_ADMIN y TENANT_OFFICE pueden actualizar branding
- WhatsApp requiere autenticación pero no bloquea MVP

## Observaciones
- Tests de integración completa pendientes de entorno de testing
- Integración real de email requiere proveedor (SendGrid/Mailgun)
- WhatsApp: evaluar API oficial de Meta antes de integrar

**Veredicto: APROBADO para HITL.**