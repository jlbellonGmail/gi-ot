# Analysis: 10-validacion-postgresql

## Resumen ejecutivo

El cambio es viable sin reescribir el producto: SQLAlchemy ya usa tipos portables y `DATABASE_URL`, pero el historial Alembic no puede reproducirse hoy sobre PostgreSQL por drift y supuestos SQLite. El Punto 10 debe corregir esos bloqueos, agregar RLS transaccional real, cerrar integridad tenant crítica, abstraer storage local y ejecutar la misma aplicación/suite en ambos motores.

## Estado base verificado

- Rama inicial: `develop`.
- `HEAD` inicial: `3d698b4183d7ae08c0f13a1c16f5e0f021270e76`.
- `origin/develop`: `3d698b4183d7ae08c0f13a1c16f5e0f021270e76`.
- `git pull --ff-only origin develop`: `Already up to date`.
- Working tree inicial: limpio.
- Rama creada: `feature/10-validacion-postgresql`.
- Alembic inicial: un HEAD `9c8b2c1d4e5f`, cadena lineal declarada.
- Python local: 3.14.7.
- Docker: cliente/servidor 29.7.2; daemon local iniciado para la validación.

## Alcance confirmado

- **Incluye**: PostgreSQL real local/CI, replay Alembic, compatibilidad de suite, RLS, contexto SQLAlchemy, constraints/índices, storage, documentación y circuito completo hasta READY_FOR_HITL.
- **Excluye**: producción, proveedor gestionado, object storage real, cambios UI, cierre post-merge del ROADMAP y Punto 11.

## Inventario técnico previo

### Configuración de base

| Área | Estado actual | Impacto |
|---|---|---|
| `Settings.database_url` | Default `sqlite:///./data/gi-ot.db`, configurable por env | Compatible en concepto. |
| Engine | `create_engine`, `check_same_thread` solo para SQLite | Base portable; falta contexto RLS. |
| Session | `sessionmaker`, una sesión por dependencia FastAPI | Adecuada para contexto por sesión/transacción. |
| Alembic | URL tomada de `Settings`; metadata importada desde `app.models` | `WorkOrderReceipt` no está exportado y existe drift. |
| Driver PostgreSQL | No declarado | Agregar `psycopg` 3. |
| Tests | SQLite en memoria con `Base.metadata.create_all` | Parametrizar para PostgreSQL y separar tests de schema migrado/RLS. |

### Tipos y consultas

| Tema | Hallazgo | Decisión |
|---|---|---|
| UUID | `uuid.UUID` + `sa.Uuid/UUID`; SQLite lo serializa, PostgreSQL usa UUID nativo | Mantener un solo modelo. |
| DateTime | Mayoría `DateTime(timezone=True)`; defaults Python UTC | Verificar round-trip aware en PostgreSQL. |
| Boolean | Modelos portables; migración de receipts usa `server_default=text('0')` | Cambiar a `sa.false()` en reparación histórica imprescindible. |
| JSON | No hay columna JSON física; `SyncOperation.payload` es TEXT serializado | No introducir JSONB fuera de alcance. |
| Text/String | Portables | Verificar tamaños y nullability reales. |
| Enum | `native_enum=False` | Compatible, sin enums PostgreSQL específicos. |
| Autoincrement | Solo `Role.id` entero | Válido en ambos motores; no es dependencia SQLite indebida. |
| SQL textual | Parciales de `User` y defaults/migraciones | Parciales ya declaran variantes SQLite/PostgreSQL; revisar defaults. |
| Búsqueda | `ilike`, casts y SQLAlchemy expressions | Ejecutar suite real PostgreSQL por diferencias de case sensitivity. |
| Correlativo OT | `max(number)+1` | Compatible pero vulnerable a concurrencia; UNIQUE por tenant detecta conflicto. Deuda no bloqueante si no falla alcance. |

### Hallazgos Alembic bloqueantes

1. `sync_operations` tiene modelo y es referenciada por revisiones 09/09c, pero ninguna revisión crea su tabla.
2. `7f8a9b2c1d4e` intenta eliminar un índice de `sync_operations` aun cuando la tabla no existe en un replay limpio.
3. `7f8a9b2c1d4e` usa defaults booleanos `0`, inválidos para boolean PostgreSQL.
4. `people(tenant_id,id)` es referenciada por FK compuesta sin constraint UNIQUE/PK compatible; PostgreSQL rechaza la FK.
5. `work_orders(tenant_id,id)` es referenciada por `WorkOrderReceipt` sin constraint UNIQUE/PK compatible; PostgreSQL rechaza la FK.
6. `WorkOrderStatus.sort_order` existe en el modelo pero no en migraciones.
7. La revisión 06 crea una FK con nombre y su downgrade intenta eliminar una constraint sin nombre/fuera del batch portable.
8. La revisión 09c vuelve a manipular un índice sync y su downgrade referencia `work_order_id`, columna inexistente del modelo actual.
9. `assets` conserva una unicidad global histórica sobre `qr_code` además del índice único tenant-scoped, contradiciendo multitenancy.

Estas correcciones no pueden postergarse únicamente a una nueva revisión cuando el replay falla antes de alcanzarla. Se permiten reparaciones quirúrgicas en las revisiones afectadas, sin cambiar datos ni semántica de negocio, y se documentan expresamente.

### Inventario tenant / RLS

| Tabla | Pertenencia | `tenant_id` | Clave/constraints actuales relevantes | Índices actuales relevantes | RLS objetivo | Justificación |
|---|---|---:|---|---|---:|---|
| `tenants` | raíz tenant | no (`id`) | PK `id` | PK | sí, política especial | Tenant solo ve su raíz; plataforma ve todas. |
| `tenant_configs` | directa | sí | UNIQUE `tenant_id` | UNIQUE | sí | Config/branding del tenant. |
| `users` | directa salvo platform owner | nullable | parciales por email | email, parciales | sí, política especial | Login/self/tenant/plataforma requieren reglas distintas. |
| `people` | directa | sí | PK `id`; falta UNIQUE `(tenant_id,id)` | tenant, nombre | sí | Datos personales tenant. |
| `person_identifications` | directa | sí | UNIQUE identificación por tenant | tenant/person | sí | Datos sensibles y deduplicación tenant. |
| `customers` | directa | sí | PK `(tenant_id,person_id)` | PK/tenant | sí | Especialización tenant. |
| `technicians` | directa | sí | PK `(tenant_id,person_id)`; user link | tenant/status/user | sí | Especialización tenant. |
| `locations` | directa | sí | FK compuesta a customer; UNIQUE nombre por customer | tenant/customer | sí | Maestro tenant. |
| `assets` | directa | sí | unicidad QR global incorrecta + tenant | tenant/location/type/QR | sí | Maestro tenant y QR aislado. |
| `asset_types` | directa | sí | UNIQUE `(tenant_id,code)` | tenant | sí | Catálogo tenant. |
| `priorities` | directa | sí | UNIQUE `(tenant_id,code)` | tenant | sí | Catálogo tenant. |
| `work_order_statuses` | directa | sí | UNIQUE `(tenant_id,code)` | tenant | sí | Catálogo tenant. |
| `work_order_types` | directa | sí | UNIQUE `(tenant_id,code)` | tenant | sí | Catálogo tenant. |
| `work_orders` | directa | sí | UNIQUE número tenant; FKs parciales tenant | tenant/status/tech/location/asset | sí | Entidad central. |
| `work_order_history` | directa | sí | FK simple a OT | tenant/OT | sí | Auditoría tenant. |
| `work_order_photos` | directa | sí | FK simple a OT | tenant/OT | sí | Metadatos de archivos tenant. |
| `work_order_receipts` | directa | sí | FK compuesta a OT | tenant/OT | sí | Comprobantes tenant. |
| `sync_operations` | directa | sí | FK simple a OT | tenant/status/entity | sí | Cola offline tenant. |
| `roles` | global | no | code único | code | no | Catálogo RBAC estable compartido. |
| `config_templates` | global | no | code único | code | no | Plantilla de plataforma. |
| `template_*` | global por template | no | UNIQUE `(template_id,code)` | template | no | Contenido de plantilla global. |

`Notification` está documentada conceptualmente, pero no existe como modelo/migración en el código actual; no se agrega en Punto 10.

### Contexto RLS propuesto

1. Antes de buscar al usuario autenticado, el backend decodifica el token firmado y guarda `app.user_id` en `Session.info`; el evento `after_begin` lo aplica con `set_config(..., true)`.
2. La política SELECT de `users` permite la fila propia por `app.user_id`, aun antes de conocer tenant.
3. Tras cargar `User` y `Role`, el backend fija `app.tenant_id` y `app.platform_admin` desde datos server-side.
4. Para login, el backend fija temporalmente `app.login_email`; solo una política SELECT permite candidatos por ese email. Las políticas de escritura no incluyen dicho contexto.
5. Un listener `SessionEvents.after_begin` reaplica los valores de `Session.info` en cada nueva transacción; esto cubre servicios actuales que hacen `commit()` y luego `refresh()`/lazy loads.
6. SQLite ignora estos helpers sin SQL específico de PostgreSQL.
7. Las políticas usan `current_setting(..., true)` + `NULLIF` para default deny si falta contexto.
8. La administración de plataforma es un bypass lógico dentro de políticas, activado únicamente tras verificar `PLATFORM_OWNER`; el rol de conexión no recibe `BYPASSRLS`.

La documentación oficial confirma que `USING` filtra filas existentes, `WITH CHECK` valida filas nuevas/modificadas, el owner normalmente elude RLS salvo `FORCE`, y `set_config(..., true)` limita el valor a la transacción. SQLAlchemy exige usar la `Connection` recibida dentro de `after_begin`.

### Archivos y almacenamiento

| Área | Estado | Riesgo/cambio |
|---|---|---|
| Fotos | Clave `{tenant}/{wo}/{uuid}.ext`, filesystem directo | La generación es aislada, pero lecturas confían en la clave DB y no validan traversal. |
| Receipts | Clave `receipts/{tenant}/...`, filesystem directo | Tenant incluido, pero orden no uniforme y APIs/SMTP dependen de `Path` local. |
| Sync photo | Construye path pero no guarda binario | Mantener semántica; eliminar imports/path sin efecto si corresponde. |
| Abstracción | No existe | Crear backend local con `save/read/delete/exists`, normalización y validación tenant. |

Las claves nuevas usarán prefijo tenant y namespaces (`<tenant>/work-orders/...`, `<tenant>/receipts/...`). La lectura conservará compatibilidad segura con claves legacy válidas sin aceptar rutas absolutas o traversal.

## Decisiones de arquitectura

- [x] Compatible con arquitectura actual: monolito modular y una API.
- [x] Requiere migración DB: sí, nueva revisión RLS/integridad más reparaciones históricas mínimas para replay.
- [x] Requiere cambios API: internos en autenticación/dependencias y serving de archivos; sin endpoints nuevos.
- [x] Requiere cambios UI: no.
- [x] Impacto offline: se preserva contrato sync y claves de fotos; tests de regresión obligatorios.
- [x] Impacto multitenancy: alto y security-critical; defensa RLS + constraints + tests directos.

## Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Replay Alembic falla antes del nuevo HEAD | Alta | Alto | Reparaciones quirúrgicas verificadas desde DB vacía en ambos motores. |
| Owner/superuser hace falso positivo en tests RLS | Alta | Crítico | Rol de prueba `NOSUPERUSER NOBYPASSRLS`, `FORCE RLS` y asserts de catálogo. |
| `SET LOCAL` desaparece tras commits internos | Alta | Crítico | `Session.info` + `after_begin`; test de commit/reapertura transaccional. |
| Login queda bloqueado antes de resolver tenant | Alta | Alto | Política SELECT específica por email, sin permisos de escritura. |
| FKs existentes permiten referencias cross-tenant | Media | Alto | FKs compuestas seleccionadas y tests de integridad. |
| Suite existente depende de SQLite | Media | Alto | Ejecutar suite completa en ambos motores y corregir solo incompatibilidades reales. |
| Storage abstraction rompe archivos legacy | Media | Medio | Compatibilidad explícita de claves legacy seguras + tests. |
| Docker/Windows difiere de runner Linux | Media | Medio | Compose portable, PostgreSQL service en CI y validación local previa. |
| Ratchet histórico usa baselines sensibles a líneas | Media | Medio | Archivos modificados deben quedar sin errores nuevos; no regenerar baselines para ocultar deuda. |
| Índices excesivos | Media | Medio | Agregar solo por FK/constraint/consulta; documentar redundancias. |

## Tasks para Builder

1. [ ] Agregar configuración reproducible PostgreSQL 17 (`compose`, ejemplos env, readiness, limpieza) y `psycopg`.
2. [ ] Reparar mínimamente las revisiones históricas bloqueantes y demostrar replay SQLite/PostgreSQL desde cero.
3. [ ] Alinear modelos/metadata con el esquema y crear una nueva revisión Alembic para drift, integridad tenant, RLS y políticas.
4. [ ] Implementar helpers de contexto RLS y listener transaccional SQLAlchemy; integrar login y autenticación.
5. [ ] Aplicar RLS/FORCE a la matriz tenant-owned y dejar globales fuera con justificación.
6. [ ] Implementar abstracción local de storage seguro; migrar fotos, receipts y serving/email sin alterar endpoints.
7. [ ] Parametrizar la suite backend para SQLite/PostgreSQL y agregar unit tests de storage/contexto.
8. [ ] Agregar tests PostgreSQL sobre schema migrado: inspección, entidades críticas, flujo API y ataques directos RLS SELECT/INSERT/UPDATE/DELETE.
9. [ ] Integrar PostgreSQL real y quality ratchet completo en `.github/workflows/ci.yml` conservando build backend/frontend.
10. [ ] Actualizar arquitectura, stack, modelo de datos y README local sin duplicación; no cerrar ROADMAP antes del merge.
11. [ ] Ejecutar gates Builder y registrar outputs reales en `runs/10-validacion-postgresql/evidence/` y `build.md`.

## Criterios de aceptación (heredados de spec.md)

- [ ] PostgreSQL real y Alembic completo desde vacío.
- [ ] SQLite y PostgreSQL usan la misma aplicación y suite crítica.
- [ ] RLS/FORCE real con rol no privilegiado.
- [ ] Operaciones cross-tenant directas bloqueadas en las cuatro clases DML.
- [ ] Integridad, índices y constraints auditados/corregidos.
- [ ] Storage portable y seguro validado.
- [ ] Regression, ratchets y builds verdes local/CI.
- [ ] Evidencia AI-NATIVE completa para HITL, sin merge.

## Referencias

- PRD: §§5, 6, 36, 39–42, 55, 62–65.
- ROADMAP: Punto 10.
- Arquitectura: §§3, 6–8, 10–11.
- Modelo datos: §§1–7, 9–10.
- Stack: Persistencia, compatibilidad, multitenancy, archivos, validación.
- UI-UX: N/A visual.
- PostgreSQL: `https://www.postgresql.org/docs/current/ddl-rowsecurity.html`, `sql-createpolicy.html`, `functions-admin.html`.
- SQLAlchemy: `https://docs.sqlalchemy.org/en/20/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin`.

## Firma

- Analyst: Codex
- Fecha: 2026-08-31
- Viabilidad: CONFIRMADA
