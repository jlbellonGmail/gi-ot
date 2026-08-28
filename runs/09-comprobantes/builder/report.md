# BUILDER — 09 Comprobantes y comunicaciones

## Construcción completada

### Backend (FastAPI)
- `apps/api/app/models/tenant.py` — Agregadas columnas de branding a TenantConfig
- `apps/api/app/models/work_order_receipt.py` — Modelo WorkOrderReceipt (HTML, PDF, tracking)
- `apps/api/app/schemas/work_order_receipt.py` — Schemas: WorkOrderReceiptOut, Generate, Send, TenantBranding, TenantBrandingUpdate, WhatsAppSend
- `apps/api/app/services/receipt.py` — ReceiptService con métodos:
  - `_get_branding()` — Obtiene branding del tenant
  - `update_branding()` — Actualiza branding del tenant
  - `generate_receipt()` — Genera HTML + PDF
  - `send_receipt_email()` — Envía por email (stub)
  - `send_receipt_whatsapp()` — Envía por WhatsApp (evaluación)
- `apps/api/app/api/v1/receipts.py` — 7 endpoints:
  - `POST /receipts` — Generar comprobante
  - `GET /{wo_id}` — HTML del comprobante
  - `GET /{wo_id}/pdf` — PDF del comprobante
  - `POST /{wo_id}/send-email` — Enviar por email
  - `POST /{wo_id}/send-whatsapp` — Enviar por WhatsApp
  - `GET /branding` — Obtener branding
  - `PUT /branding` — Actualizar branding

### Frontend
- `apps/web/src/app/layout.tsx` — OfflineStatusBanner agregado

### Tests
- `apps/api/tests/test_offline_recovery.py` — 4 tests de recuperación offline

### Dependencias
- `fpdf2` — Generación de PDF
- `jinja2` — Templates HTML

### Commits
- `ba08628` — feat: punto 09 (completo)
- `430b35e` — feat: punto 09 (inicial)
- `93cd81e` — feat: punto 09 (models/schemas)

**Construcción completada exitosamente.**