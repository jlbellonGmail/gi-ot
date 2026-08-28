# SPEC — 09 Comprobantes y comunicaciones

## 1. Contexto
Implementar generación de comprobantes de OT, branding por tenant, envío por email y evaluación de WhatsApp (ROADMAP §09).

## 2. Alcance
- [x] Generar comprobante de OT (HTML + PDF)
- [x] Branding básico por tenant (logo, colores, datos empresa)
- [x] Envío por email
- [x] Evaluar WhatsApp según decisión técnica y comercial

## 3. Out of Scope
- WhatsApp no bloquea MVP inicial
- Integración real de email (stub listo para proveedor)
- Geolocalización
- Firma digital

## 4. Contrato observable
- `POST /api/v1/receipts` → genera comprobante (HTML + PDF)
- `GET /api/v1/receipts/{wo_id}` → HTML del comprobante
- `GET /api/v1/receipts/{wo_id}/pdf` → PDF del comprobante
- `POST /api/v1/receipts/{wo_id}/send-email` → envía por email
- `POST /api/v1/receipts/{wo_id}/send-whatsapp` → envía por WhatsApp (evaluación)
- `GET /api/v1/receipts/branding` → obtiene branding del tenant
- `PUT /api/v1/receipts/branding` → actualiza branding del tenant

## 5. Modelo
- `WorkOrderReceipt`: comprobante por OT (HTML, PDF, tracking envíos)
- `TenantConfig`: columnas de branding (logo_url, primary_color, secondary_color, address, phone, email, website, tax_id)

## 6. Criterios de aceptación
- Comprobante se genera solo para OT en estado terminal
- Branding se aplica del TenantConfig
- PDF se genera y guarda en storage
- Email/WhatsApp marcan como enviado (stub listo para proveedor)
- Branding actualizable via API

## 7. Riesgos
- Integración real de email requiere proveedor (SendGrid, Mailgun, etc.)
- WhatsApp requiere API oficial de Meta (evaluación comercial)

## 8. Referencias
- `docs/producto/PRD.md` §47, §54
- `docs/tecnica/arquitectura.md` §7
- `docs/ui-ux/UI-UX-STANDARDS.md`