# Arquitectura v0.1 — gi-ot

**Estado:** BOOTSTRAP
**Depende de:** `docs/tecnica/stack.md`, `docs/producto/modelo-funcional.md`
**Documento:** `docs/tecnica/arquitectura.md`

Define la arquitectura mínima necesaria para construir el MVP descrito en el PRD y el modelo funcional. No introduce infraestructura distribuida, microservicios ni componentes sin necesidad demostrada, conforme a `AGENTS.md` y `stack.md`.

---

## 1. Vista general

```text
┌─────────────────────────────┐
│   Next.js / PWA (apps/web)  │
│   mobile-first, offline     │
└──────────────┬───────────────┘
               │ HTTPS / REST /api/v1
               ▼
┌─────────────────────────────┐
│   FastAPI (apps/api)        │
│   monolito modular          │
└──────────────┬───────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────┐
│ SQLite (BOOTSTRAP)          │
│ PostgreSQL (producción)     │
└─────────────────────────────┘
```

Un solo frontend y una sola API sirven a todos los tenants. La PWA nunca accede a la base de datos directamente: toda regla de negocio y todo control de acceso pasa por la API.

---

## 2. Monolito modular (apps/api)

La API se organiza en módulos internos alineados con el modelo funcional, no en servicios separados:

```text
apps/api/
  core/          # config, seguridad, resolución de tenant, dependencias comunes
  auth/          # autenticación, sesiones/tokens
  tenants/       # Tenant, TenantConfig
  users/         # User, Role
  catalog/       # AssetType, WorkOrderStatus, WorkOrderType, Priority (parametrización)
  people/        # Person, PersonIdentification y sus especializaciones de
                 # negocio (Customer, Technician); expone endpoints de
                 # negocio "clientes" y "tecnicos" — Person nunca se expone
                 # directamente (modelo-datos.md §10)
  locations/     # Location, Asset (Location referencia Customer)
  workorders/    # WorkOrder, WorkOrderPhoto, WorkOrderHistory
  notifications/ # Notification
  sync/          # SyncOperation, endpoints de sincronización offline
  files/         # almacenamiento y referencia de fotos/archivos
```

Cada módulo expone routers REST bajo `/api/v1/...` y contiene sus propios modelos SQLAlchemy, schemas Pydantic y reglas de negocio. Los módulos pueden depender de `core` y `tenants`, pero no deben depender unos de otros de forma circular. Esta separación es lógica, dentro de un único proceso desplegable — no son microservicios.

Esta estructura es deliberadamente la misma que usarán los módulos futuros del ecosistema (facturación, stock, CRM — PRD §59): se agregan como nuevos paquetes dentro del monolito o, más adelante, como servicios independientes que consumen la misma API, sin reescribir el núcleo.

---

## 3. Multitenancy: resolución y aislamiento

### 3.1 Modelo

`shared database + shared schema + tenant_id`, tal como fija `stack.md`. Toda tabla de negocio (clients, locations, assets, work_orders, etc.) incluye una columna `tenant_id` obligatoria.

### 3.2 Resolución del tenant activo

El tenant **nunca** se toma de un parámetro enviado por el cliente (body, query string, header manipulable). Se resuelve siempre a partir de la identidad autenticada:

```text
Request
  │
  ▼
Token/sesión válida
  │
  ▼
User → tenant_id asociado en backend
  │
  ▼
tenant_id de contexto para la request
  │
  ▼
Toda query se filtra por ese tenant_id
```

Excepción: `PLATFORM_OWNER` no tiene `tenant_id` propio y opera sobre endpoints de plataforma separados (gestión de tenants), nunca sobre endpoints de negocio de un tenant.

### 3.3 Cómo se aplica el filtrado

* Una dependencia común de FastAPI (`core`) resuelve el `tenant_id` de la request autenticada y lo inyecta en cada handler.
* El acceso a datos pasa por funciones/repositorios que exigen `tenant_id` como parte de toda consulta — no se permite una consulta a estas tablas sin ese filtro.
* Ninguna entidad puede referenciar una fila de otro tenant (ej.: una `WorkOrder` no puede apuntar a un `Client` de otro tenant); esto se valida en la capa de negocio al crear/actualizar relaciones.

### 3.4 Row-Level Security (futuro, producción)

En SQLite (BOOTSTRAP) el aislamiento se garantiza exclusivamente en la capa de aplicación, porque SQLite no soporta RLS. Al migrar a PostgreSQL (ROADMAP etapa 10), se agrega RLS como defensa en profundidad:

* política RLS por tabla de negocio basada en `tenant_id = current_setting('app.tenant_id')`;
* la aplicación sigue filtrando explícitamente por `tenant_id` (RLS no sustituye el filtrado en la capa de negocio, lo refuerza);
* la sesión de base de datos setea `app.tenant_id` al inicio de cada request autenticada.

### 3.5 Prueba obligatoria

Debe existir un test automatizado que confirme que un usuario del Tenant A nunca puede leer ni modificar datos del Tenant B, cubriendo al menos: personas (clientes y técnicos), ubicaciones, activos y OT (PRD §65, punto 22).

### 3.6 Personas y especializaciones de negocio

`Customer` y `Technician` no son entidades independientes: son especializaciones de una base común `Person`, para que una misma persona real (p. ej. cliente y técnico a la vez) nunca quede duplicada. El detalle del modelo, la búsqueda por identificación, la creación transaccional y la distinción frente a los roles RBAC están en `modelo-datos.md` §10 — este documento no lo repite.

Consecuencia arquitectónica: el módulo `people` (sección 2) es el único que crea o modifica `Person`; los endpoints de negocio (`/clientes`, `/tecnicos`) nunca exponen el concepto `Person` al frontend, solo las especializaciones.

---

## 4. Autenticación y autorización

* Autenticación gestionada por el backend (FastAPI), sin depender de proveedores externos de auth.
* Contraseñas nunca en texto plano (hash con algoritmo estándar, p. ej. bcrypt/argon2).
* Sesión de usuario mediante token (p. ej. JWT) que identifica `user_id`; el `tenant_id` se resuelve en backend a partir de ese `user_id`, nunca se confía en un `tenant_id` que viaje en el token editable por el cliente sin validación adicional del lado servidor.
* Autorización mediante RBAC con los cuatro roles fijados en el PRD y `stack.md`. Los permisos por rol se verifican siempre en el backend; el frontend solo oculta/muestra UI como conveniencia, nunca como control de seguridad.

---

## 5. Parametrización

`TenantConfig` y los catálogos del módulo `catalog` (`WorkOrderStatus`, `Priority`, `WorkOrderType`, `AssetType`) separan:

* **semántica interna estable** — un código fijo usado por la lógica de negocio (`PENDING`, `URGENT`, etc.);
* **etiqueta visible** — el texto configurado por cada tenant.

Estos catálogos se modelan como tablas con `tenant_id`, sembradas con valores por defecto al crear el tenant, y editables por `TENANT_ADMIN` sin requerir despliegue de código.

---

## 6. Persistencia: SQLite → PostgreSQL

* SQLAlchemy 2.x como capa de acceso a datos y Alembic para migraciones, en ambos entornos.
* Se evita SQL específico de SQLite; los tipos de columna y constraints se eligen por compatibilidad con PostgreSQL desde el día uno (stack.md).
* Identificadores de entidades principales en UUID.
* El cambio de motor (BOOTSTRAP → producción) se resuelve mediante configuración de conexión (`DATABASE_URL`) y ejecución de las mismas migraciones Alembic sobre PostgreSQL — no implica cambios en modelos de dominio ni en la lógica de negocio (ROADMAP etapa 10).

---

## 7. Archivos y fotografías

* BOOTSTRAP: almacenamiento en filesystem local (`data/uploads/`), referenciado desde `WorkOrderPhoto` mediante ruta/URL relativa.
* Producción: Object Storage S3-compatible; la base de datos conserva únicamente metadatos y referencia (clave del objeto), nunca el binario.
* La ruta de acceso a un archivo siempre pasa por la API, que valida pertenencia al tenant antes de servir o firmar la URL — nunca se expone un archivo de un tenant por adivinación de ruta.

---

## 8. Offline y sincronización

### 8.1 Frontend

* Service Worker para cache de assets y app shell (instalación PWA).
* IndexedDB para datos de negocio necesarios en campo (OT asignadas, catálogos del tenant, clientes/ubicaciones/activos relevantes) y para la cola de operaciones pendientes.
* Toda operación de escritura del técnico (iniciar, registrar, adjuntar foto, cerrar) se guarda primero en local y se marca como pendiente de sincronizar.

### 8.2 Cola de sincronización (`sync`)

```text
Acción del técnico (offline)
        ↓
Se guarda en IndexedDB + se encola (SyncOperation)
        ↓
Vuelve la conectividad
        ↓
El cliente envía las SyncOperation pendientes a /api/v1/sync
        ↓
API aplica cada operación (idempotente, validando tenant y OT)
        ↓
Confirmación → se marca sincronizado en local
```

* `SyncOperation` registra tipo de operación, entidad afectada, payload, estado (`pending`, `synced`, `error`) y pertenece al `tenant_id` del usuario que la generó.
* La sincronización es responsabilidad exclusiva del backend vía API; no hay replicación directa de base de datos al dispositivo.
* La UI comunica siempre el estado real (`Sincronizado`, `Pendiente`, `Sincronizando`, `Error`) — nunca debe mostrar como confirmado algo que solo existe en local (PRD §41).

### 8.3 Conflictos

Como cada OT tiene un único técnico responsable (modelo funcional §5), los conflictos de edición concurrente son infrecuentes por diseño. El backend igualmente detecta conflictos evidentes (p. ej. una OT ya cerrada por otra vía) y los registra en `WorkOrderHistory` en lugar de sobreescribir silenciosamente. No se construye un motor de resolución de conflictos genérico en el MVP.

---

## 9. Límites entre módulos

* `apps/web` (PWA) solo conoce la API REST versionada; no conoce el modelo de datos interno.
* `apps/api` no expone detalles de implementación (SQLAlchemy, filesystem) fuera de su propia capa de acceso a datos.
* Los módulos internos de `apps/api` (sección 2) se comunican mediante llamadas de función/servicio dentro del mismo proceso — no colas, no eventos, no brokers.
* Todo módulo que accede a datos de negocio exige `tenant_id` de contexto; ningún módulo implementa su propio mecanismo paralelo de resolución de tenant.

---

## 10. Desarrollo local

```text
apps/web  (Next.js dev server)
     +
apps/api  (FastAPI/uvicorn)
     +
SQLite (archivo local)
     +
data/uploads/ (filesystem local)
```

Sin Docker, sin PostgreSQL local, sin servicios cloud obligatorios — conforme a `stack.md`. Variables de entorno (`.env`, no versionado) para configuración sensible (secret de firma de tokens, `DATABASE_URL`, rutas de storage).

---

## 11. Producción objetivo

```text
Next.js / PWA (Vercel)
        │  HTTPS
        ▼
FastAPI (contenedor independiente)
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL  Object Storage
(RLS)       (S3-compatible)
```

* Backend en un contenedor independiente (proveedor a decidir).
* PostgreSQL administrado, con RLS activado (sección 3.4).
* Object Storage S3-compatible para archivos (sección 7).
* HTTPS, backups y logging/monitoreo básico como requisitos de despliegue (ROADMAP etapa 13), sin agregar componentes de observabilidad distribuida en esta etapa.

---

## 12. Explícitamente fuera de esta arquitectura

Conforme a `stack.md` y `AGENTS.md`, no se incorporan sin necesidad demostrada: microservicios, Kubernetes, Redis, brokers de mensajería (RabbitMQ/Kafka), Elasticsearch, GraphQL, CQRS, event sourcing, ni aplicaciones móviles nativas. Cualquier incorporación futura de estas piezas requiere decisión explícita y actualización de este documento y de `stack.md`.
