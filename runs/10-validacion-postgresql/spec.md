# SPEC: 10-validacion-postgresql

## Contexto

- **PRD**: secciones 5, 6, 36, 39–42, 55, 62–65.
- **ROADMAP**: Punto 10 — Validación PostgreSQL.
- **Problema**: la aplicación fue construida y probada principalmente sobre SQLite. Antes del piloto debe demostrarse, con PostgreSQL real, que el historial Alembic, el dominio, el aislamiento multitenant, los archivos y los gates de calidad funcionan sin una reescritura del producto.

## Alcance

### Incluye

- [ ] Entorno local reproducible de PostgreSQL 17 para validación, con healthcheck, configuración por variables de entorno e instrucciones de limpieza.
- [ ] Driver `psycopg` y selección del motor exclusivamente mediante `DATABASE_URL`.
- [ ] Ejecución del historial Alembic completo sobre una base PostgreSQL vacía, inspección del esquema y verificación de coherencia hasta un único HEAD.
- [ ] Correcciones mínimas a incompatibilidades históricas que impiden reproducir el historial y una migración nueva para cambios propios del Punto 10.
- [ ] Compatibilidad funcional SQLite/PostgreSQL mediante la misma suite backend y tests PostgreSQL específicos.
- [ ] Row-Level Security de PostgreSQL como defensa en profundidad para tablas tenant-owned, sin eliminar filtros de aplicación.
- [ ] Contexto de tenant, usuario, login y administración de plataforma derivado en backend y aplicado de forma transaccional a SQLAlchemy.
- [ ] `ENABLE ROW LEVEL SECURITY` y `FORCE ROW LEVEL SECURITY`, con `USING` y `WITH CHECK` explícitos.
- [ ] Pruebas directas contra PostgreSQL que omiten filtros ORM deliberadamente y cubren SELECT, INSERT, UPDATE y DELETE cross-tenant.
- [ ] Auditoría y corrección justificada de índices, nullability, FK, UNIQUE y constraints de pertenencia tenant.
- [ ] Validación de Tenant, User, Person, Customer, Technician, Location, Asset, catálogos, WorkOrder, WorkOrderHistory, WorkOrderPhoto, WorkOrderReceipt, TenantConfig y SyncOperation.
- [ ] Abstracción local pequeña de almacenamiento basada en claves relativas seguras, aisladas por tenant y portable a object storage.
- [ ] PostgreSQL real en GitHub Actions sin degradar los gates AI-NATIVE ni el quality ratchet.
- [ ] Documentación canónica estrictamente necesaria y evidencias del circuito en `runs/10-validacion-postgresql/`.

### No incluye (fuera de scope)

- [ ] Provisión o despliegue de PostgreSQL productivo/administrado.
- [ ] Elección o despliegue de S3, R2, Azure Blob u otro proveedor de object storage.
- [ ] Eliminación de SQLite como opción legítima de desarrollo local.
- [ ] Reescritura del dominio, cambio de stack, microservicios o cambios visuales de frontend.
- [ ] Cierre definitivo del Punto 10 en `ROADMAP.md` antes del merge.
- [ ] Inicio o implementación del Punto 11.

## Comportamiento

### Reglas funcionales específicas

1. La misma API debe funcionar con SQLite o PostgreSQL según `DATABASE_URL`; no existirán variantes de producto por motor.
2. El contexto RLS se deriva de identidad autenticada y estado servidor. Ningún `tenant_id` enviado por el cliente configura RLS.
3. En PostgreSQL, cada transacción de una sesión autenticada recibe contexto local de usuario/tenant; el contexto se reaplica después de `commit` o `rollback` cuando SQLAlchemy abre otra transacción.
4. La autenticación solo puede habilitar visibilidad temporal de las filas candidatas por el email recibido; dicho contexto no autoriza INSERT, UPDATE ni DELETE.
5. Las tablas tenant-owned aplican RLS a SELECT, INSERT, UPDATE y DELETE. Las tablas globales de plataforma quedan fuera con justificación explícita.
6. El owner de tabla no debe eludir las políticas durante tráfico normal: las tablas protegidas usan `FORCE ROW LEVEL SECURITY` y las pruebas verifican un rol sin `SUPERUSER` ni `BYPASSRLS`.
7. La administración de plataforma usa un contexto explícito que solo se activa después de comprobar server-side el rol `PLATFORM_OWNER`.
8. Las claves de archivos nuevas son relativas, no contienen traversal y llevan el tenant como prefijo. La API valida la pertenencia tenant antes de leer o borrar.
9. Las migraciones históricas solo se ajustan cuando una incompatibilidad impide ejecutar la historia real desde cero; toda corrección se documenta y no reescribe reglas de negocio.
10. Los cambios de índices y constraints deben tener una justificación de aislamiento, integridad o consulta real.

### Excepciones justificadas

- SQLite no ejecuta RLS porque no lo soporta; mantiene aislamiento en aplicación y corre la suite de regresión.
- `Role`, `ConfigTemplate` y las tablas `Template*` son catálogos globales, por lo que no reciben RLS tenant.
- El entorno reproducible usa credenciales exclusivamente locales/de CI provistas por variables; no son credenciales de producción y no se versionan secretos reales.
- No se modifica la UI; la validación frontend se limita a lint/typecheck/build y regresión de integración contractual.

## Interfaces afectadas

### API Endpoints

| Método | Path | Descripción |
|---|---|---|
| POST | `/api/v1/auth/login` | Establece contexto de login limitado antes de resolver identidad. |
| Todos autenticados | `/api/v1/*` | Reutilizan la sesión SQLAlchemy con contexto RLS derivado server-side. |
| GET | Rutas de fotos/PDF existentes | Leen bytes mediante abstracción de storage y validación de clave tenant. |

No se agregan endpoints públicos nuevos.

### UI Components

N/A — no hay cambios visuales ni funcionales de UI.

### DB Schema

| Área | Cambio | Migración |
|---|---|---|
| Historia existente | Reparaciones portables imprescindibles para replay PostgreSQL | revisiones históricas afectadas, documentadas en `build.md` |
| Tablas tenant-owned | RLS, políticas, `FORCE ROW LEVEL SECURITY` | nueva revisión del Punto 10 |
| Integridad tenant | UNIQUE/FK compuestas y eliminación de unicidad global incorrecta donde corresponda | nueva revisión del Punto 10 |
| Drift modelo/esquema | Columnas/índices faltantes comprobados contra metadata | nueva revisión del Punto 10 |

## Datos

### Modelos nuevos/modificados

- Modelos tenant-owned: constraints compuestas necesarias para impedir referencias cross-tenant.
- `User`: política RLS especial para autenticación, identidad propia, tenant y plataforma.
- Storage de `WorkOrderPhoto` y `WorkOrderReceipt`: claves seguras y tenant-scoped.
- `SyncOperation`: presencia real en Alembic y RLS.

### Migraciones requeridas

- Una nueva revisión Alembic posterior al HEAD actual para RLS, constraints, índices y drift confirmado.
- Reparación excepcional y mínima de revisiones previas únicamente si el replay vacío falla antes de alcanzar el nuevo HEAD.
- Upgrade desde base vacía, downgrade de la revisión nueva y re-upgrade verificados en SQLite y PostgreSQL donde aplique.

## Seguridad

### Multitenancy

- Los filtros explícitos existentes permanecen.
- PostgreSQL RLS agrega una segunda frontera independiente de filtros ORM.
- `USING` limita filas existentes; `WITH CHECK` bloquea filas nuevas o modificadas de otro tenant.
- Tests directos SQL demuestran que una consulta sin `tenant_id` solo ve el tenant activo.

### Permisos (RBAC)

| Contexto | Alcance DB permitido |
|---|---|
| Usuario tenant autenticado | Filas del tenant derivado server-side. |
| Login no autenticado | SELECT temporal de candidatos por email; ninguna escritura. |
| `PLATFORM_OWNER` autenticado | Bypass lógico explícito mediante política, sin atributo PostgreSQL `BYPASSRLS`. |
| Migraciones | Rol de validación controlado; no representa tráfico tenant. |

### Validaciones

- Contexto mediante `set_config(..., true)` para alcance transaccional.
- Identificadores convertidos/parametrizados por SQLAlchemy; sin concatenar input en SQL.
- Storage keys normalizadas y rechazadas si son absolutas, contienen `..`, separadores inválidos o no pertenecen al tenant.
- Credenciales únicamente en variables de entorno/secretos de CI.

## Tests requeridos

### Unitarios

- [ ] Storage: claves válidas, aislamiento, rechazo de path traversal y compatibilidad de lectura local.
- [ ] Contexto RLS: no-op seguro en SQLite y persistencia de identidad en `Session.info`.

### Integración

- [ ] Suite backend completa sobre SQLite.
- [ ] Suite backend completa sobre PostgreSQL real.
- [ ] Alembic desde base PostgreSQL vacía hasta HEAD.
- [ ] Inspección PostgreSQL de tablas, PK/FK, UNIQUE, índices, políticas y flags RLS/FORCE.
- [ ] Flujo autenticado crítico con la base migrada y RLS activo.
- [ ] A lee A y B lee B.
- [ ] A no lee B; B no lee A mediante SQL directo sin filtro ORM.
- [ ] A no inserta filas con `tenant_id` B.
- [ ] A no actualiza ni elimina filas B.
- [ ] Constraints impiden referencias tenant fraudulentas en relaciones críticas.
- [ ] Entidades críticas, comprobantes y sync operan en PostgreSQL.

### E2E/UI (si aplica)

- [ ] N/A visual; frontend lint, typecheck y build deben permanecer verdes.

## Criterios de aceptación

- [ ] PostgreSQL real informa versión y readiness y se levanta con un procedimiento reproducible.
- [ ] `alembic heads`, `history`, `current` y `upgrade head` demuestran una historia lineal coherente desde base vacía.
- [ ] El esquema migrado contiene todas las entidades críticas y coincide con metadata SQLAlchemy sin drift bloqueante.
- [ ] Suite completa verde sobre SQLite y PostgreSQL real.
- [ ] RLS activo y forzado en todas las tablas tenant-owned inventariadas; tablas globales justificadas.
- [ ] Rol de prueba PostgreSQL no es superusuario ni tiene `BYPASSRLS`.
- [ ] Cross-tenant SELECT, INSERT, UPDATE y DELETE quedan bloqueados por PostgreSQL aun sin filtros ORM.
- [ ] Contexto RLS persiste correctamente al abrir nuevas transacciones después de commits.
- [ ] Índices, UNIQUE, FK, nullability y cascadas se auditan y las incompatibilidades críticas se corrigen.
- [ ] Archivos usan claves portables, tenant-scoped y sin traversal; DB no contiene binarios.
- [ ] Quality ratchet Ruff/mypy/ESLint/TypeScript no incorpora deuda nueva.
- [ ] Build backend y frontend verdes.
- [ ] CI del PR ejecuta PostgreSQL real y todos los checks terminan verdes.
- [ ] Artefactos AI-NATIVE completos, evidencia coherente con el SHA final, working tree limpio y `develop` sin merge de la feature.

## Referencias transversales

- `docs/ui-ux/UI-UX-STANDARDS.md` — N/A visual; se preserva el contrato UI existente.
- `docs/tecnica/arquitectura.md` — §§3, 6, 7, 8, 10 y 11.
- `docs/tecnica/modelo-datos.md` — §§1–7, 9 y 10.
- `docs/tecnica/stack.md` — Persistencia, compatibilidad, multitenancy, archivos y validación.
- `docs/producto/PRD.md` — §§5, 6, 36, 39–42, 55, 62–65.
- `ROADMAP.md` — Punto 10 exclusivamente.
- `AGENTS.md` — AI-NATIVE, multitenancy, seguridad, offline, tests y documentación.
- PostgreSQL — Row Security Policies, CREATE POLICY, `current_setting`/`set_config`.
- SQLAlchemy 2.x — `SessionEvents.after_begin`.

---

## Checklist pre-Analyst

- [x] Problema claro y acotado
- [x] Alcance realista
- [x] Dependencias identificadas
- [x] Riesgos listados

## Checklist pre-Reviewer

- [x] Spec completo
- [x] Referencias transversales correctas
- [x] No duplica docs transversales
- [x] Criterios de aceptación verificables

## Checklist pre-Builder

- [ ] Review APROBADO
- [x] Tasks claras en analysis.md
- [ ] Spec inmutable (no modificar)

## Checklist pre-QA

- [ ] Build.md completo
- [ ] Tests escritos
- [ ] Suite completa pasa

## Checklist pre-Code Reviewer

- [ ] QA PASS
- [ ] Código listo para revisión

## Checklist pre-HITL

- [ ] Todos los gates verdes
- [ ] Evidencia completa en runs/
- [ ] CI verde en PR
