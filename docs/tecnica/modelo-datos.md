# Modelo de datos v0.1 — gi-ot

**Estado:** BOOTSTRAP
**Depende de:** `docs/tecnica/arquitectura.md`, `docs/producto/modelo-funcional.md`
**Documento:** `docs/tecnica/modelo-datos.md`

Modelo conceptual de persistencia. No incluye SQL físico ni migraciones Alembic — eso corresponde a la etapa de construcción.

---

## 1. Convenciones generales

* Clave primaria: `id` (UUID) en todas las entidades, salvo donde se indique lo contrario.
* Toda entidad de negocio (todo lo que no sea `Tenant` mismo o catálogo de plataforma) incluye `tenant_id` como FK obligatoria a `Tenant`, con índice.
* Auditoría mínima común: `created_at`, `created_by`, `updated_at`, `updated_by` en toda entidad mutable (PRD §56).
* Tipos y constraints elegidos por compatibilidad SQLite/PostgreSQL: evitar tipos específicos de un motor; usar `TEXT`/`VARCHAR`, `TIMESTAMP`, `BOOLEAN`, `UUID` (como `TEXT` en SQLite, `UUID` nativo en PostgreSQL vía SQLAlchemy).
* Los catálogos parametrizables (`WorkOrderStatus`, `Priority`, `WorkOrderType`, `AssetType`) separan siempre un `code` interno estable de un `label` visible editable por tenant.
* Excepción a la PK simple: las especializaciones de negocio de `Person` (`Customer`, `Technician`, y futuras) usan clave primaria compuesta `(tenant_id, person_id)`, que es simultáneamente FK hacia `Person(tenant_id, id)` — ver §10.

---

## 2. Entidades y pertenencia a tenant

| Entidad | `tenant_id` | Notas |
|---|---|---|
| Tenant | — (es la raíz) | |
| TenantConfig | sí (1:1 con Tenant) | |
| User | sí, salvo `PLATFORM_OWNER` | `PLATFORM_OWNER` tiene `tenant_id` nulo |
| Role | no (catálogo fijo de plataforma) | los 4 roles base no son parametrizables |
| ConfigTemplate | no (catálogo de plataforma) | plantilla de configuración inicial, ver §9 |
| TemplatePriority / TemplateWorkOrderType / TemplateWorkOrderStatus / TemplateAssetType | no (`template_id`, no `tenant_id`) | contenido de una `ConfigTemplate`, ver §9 |
| Person | sí | base común de datos de persona, ver §10 |
| PersonIdentification | sí | múltiples identificaciones por `Person`, ver §10 |
| Customer | sí (PK compuesta `(tenant_id, person_id)`, FK a `Person`) | especialización de `Person` — ver §10 |
| Technician | sí (PK compuesta `(tenant_id, person_id)`, FK a `Person`) | especialización de `Person`, independiente de `User` — ver §10 |
| Location | sí (heredado de Customer) | |
| Asset | sí (heredado de Location) | |
| AssetType | sí | catálogo parametrizable |
| WorkOrder | sí | |
| WorkOrderStatus | sí | catálogo parametrizable |
| WorkOrderType | sí | catálogo parametrizable |
| Priority | sí | catálogo parametrizable |
| WorkOrderPhoto | sí (heredado de WorkOrder) | |
| WorkOrderHistory | sí (heredado de WorkOrder) | |
| Notification | sí | |
| SyncOperation | sí | |

Toda entidad marcada "sí" exige `tenant_id` en cada fila y en cada consulta, conforme a `arquitectura.md` §3.

---

## 3. Diagrama de relaciones

```text
Tenant (1) ──── (1) TenantConfig

Tenant (1) ──── (N) User
Tenant (1) ──── (N) Person
Tenant (1) ──── (N) AssetType
Tenant (1) ──── (N) WorkOrderStatus
Tenant (1) ──── (N) WorkOrderType
Tenant (1) ──── (N) Priority
Tenant (1) ──── (N) WorkOrder
Tenant (1) ──── (N) Notification
Tenant (1) ──── (N) SyncOperation

User (N) ──── (1) Role

Person (1) ──── (N) PersonIdentification
Person (1) ──── (0..1) Customer        # especialización, PK compartida
Person (1) ──── (0..1) Technician      # especialización, PK compartida
# futuras especializaciones (Supplier, Partner, Owner, ...) seguirán el
# mismo patrón 1 ──── (0..1) sin modificar Person (§10)

Customer (1) ──── (N) Location
Location (1) ──── (N) Asset
AssetType (1) ──── (N) Asset

WorkOrder (N) ──── (1) Customer
WorkOrder (N) ──── (1) Location
WorkOrder (N) ──── (1) Asset
WorkOrder (N) ──── (1) Technician
WorkOrder (N) ──── (1) WorkOrderStatus
WorkOrder (N) ──── (1) WorkOrderType
WorkOrder (N) ──── (1) Priority
WorkOrder (1) ──── (N) WorkOrderPhoto
WorkOrder (1) ──── (N) WorkOrderHistory

SyncOperation (N) ──── (1) User        # quién generó la operación offline
```

---

## 4. Entidades

### 4.1 Tenant

Raíz de aislamiento. No tiene `tenant_id`.

Campos: `id`, `name`, `commercial_name`, `status` (activo/suspendido), `created_at`, `updated_at`.

### 4.2 TenantConfig

Configuración 1:1 con Tenant: branding básico (nombre comercial mostrado, logo, colores), datos de comprobante, preferencias operativas, canal de notificación por defecto.

Campos: `id`, `tenant_id` (FK única), `branding` (estructura flexible: JSON o columnas simples según necesidad real), `updated_at`.

### 4.3 User

Cuenta de acceso al sistema.

Campos: `id`, `tenant_id` (nulo solo para `PLATFORM_OWNER`), `email` (único por tenant), `password_hash`, `role_id`, `full_name`, `status` (activo/inactivo), `created_at`, `updated_at`.

Restricción: `email` único dentro del mismo `tenant_id`; `PLATFORM_OWNER` único globalmente por email.

### 4.4 Role

Catálogo fijo de plataforma, no parametrizable: `PLATFORM_OWNER`, `TENANT_ADMIN`, `TENANT_OFFICE`, `TENANT_TECHNICIAN`. Sin `tenant_id`.

Campos: `id`, `code` (estable, usado por la lógica), `default_label` (texto por defecto, potencialmente sobreescrito visualmente por `TenantConfig` sin alterar `code`).

### 4.5 Person

Entidad base compartida por todas las especializaciones de negocio (`Customer`, `Technician`, y futuras — ver §10). Contiene los datos generales de una persona física o jurídica **una sola vez por tenant**, sin importar cuántas especializaciones tenga.

Campos: `id` (identifica a la persona; referenciado como `person_id` desde las especializaciones), `tenant_id`, `person_type` (física/jurídica), `display_name` (nombre o razón social), `address`, `phone`, `email`, `notes`, `status` (activo/inactivo), auditoría.

No incluye ningún campo propio de una especialización (§10.3).

### 4.6 PersonIdentification

Identificaciones de una `Person` (documento nacional, identificación tributaria, u otro según país). Nunca se usa como PK técnica.

Campos: `id`, `tenant_id`, `person_id` (FK a `Person(tenant_id, id)`), `country_code` (ISO 3166-1 alpha-2, p. ej. `AR`), `identification_type` (código estable e internacionalizable, p. ej. `DNI`, `CUIT` — no atado a nombres de un único país), `identification_value`, `is_primary` (booleano).

Restricción: `UNIQUE(tenant_id, country_code, identification_type, identification_value)` — impide registrar dos veces la misma identificación dentro de un tenant (§10.4). Una `Person` admite múltiples identificaciones (p. ej. DNI y CUIT simultáneos en Argentina).

### 4.7 Customer

Especialización de `Person` para el rol comercial de cliente (sustituye al concepto antes descrito como `Client`).

Clave: `(tenant_id, person_id)` — PK y FK simultánea hacia `Person(tenant_id, id)`.

Campos propios: ninguno obligatorio en el MVP; la tabla existe para marcar la especialización y admitir atributos exclusivamente comerciales en el futuro sin tocar `Person`.

Nunca duplica `display_name`, `address`, `phone` ni `email` — esos viven únicamente en `Person` (§10.3).

### 4.8 Technician

Especialización de `Person` para el rol operativo de técnico. Ya no extiende a `User`: una `Person` puede ser `Technician` sin tener acceso al sistema, y un `User` con rol `TENANT_TECHNICIAN` no implica necesariamente una fila `Technician` — son conceptos independientes (§10.9).

Clave: `(tenant_id, person_id)` — PK y FK simultánea hacia `Person(tenant_id, id)`.

Campos propios: `profession` (opcional), `license_number` (matrícula, opcional), `commission_percentage` (opcional), `status` (activo/inactivo).

Nunca duplica datos generales de `Person`.

### 4.9 Location

Campos: `id`, `tenant_id`, `customer_id` (FK a `Customer`), `name`, `address`, `city`, `province`, `notes`, auditoría.

Restricción: `customer_id` debe pertenecer al mismo `tenant_id` que la `Location` (validado en capa de negocio).

### 4.10 Asset

Campos: `id`, `tenant_id`, `location_id` (FK), `asset_type_id` (FK, opcional), `name`, `description`, `brand`, `model`, `serial_number`, `internal_code`, `qr_code` (identificador seguro, opcional), `status`, `notes`, auditoría.

Restricción: solo `name` es obligatorio; el resto admite nulo (PRD §24). `location_id` y `asset_type_id` deben pertenecer al mismo `tenant_id`.

### 4.11 AssetType

Catálogo parametrizable por tenant.

Campos: `id`, `tenant_id`, `code` (interno, único por tenant), `label` (visible), `active`.

### 4.12 WorkOrder

Entidad central.

Campos: `id`, `tenant_id`, `number` (correlativo por tenant), `customer_id`, `location_id`, `asset_id`, `technician_id` (responsable principal, opcional hasta asignación), `work_order_type_id`, `priority_id`, `status_id`, `requested_description`, `performed_description`, `scheduled_at` (opcional), `started_at`, `finished_at`, `created_by`, `created_at`, `updated_by`, `updated_at`.

Restricciones:

* `number` único dentro del `tenant_id`.
* `customer_id`, `location_id`, `asset_id`, `technician_id`, `work_order_type_id`, `priority_id`, `status_id` deben pertenecer todos al mismo `tenant_id` que la `WorkOrder` — validado en capa de negocio, no delegado únicamente a la FK.
* `location_id` debe pertenecer a `customer_id`; `asset_id` debe pertenecer a `location_id`.
* Una `WorkOrder` con `status` terminal (terminada/no resuelta) no admite edición directa de sus campos de ejecución salvo a través de una reapertura (ver `WorkOrderHistory`).

### 4.13 WorkOrderStatus

Catálogo parametrizable por tenant, con semántica interna estable.

Campos: `id`, `tenant_id`, `code` (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `UNRESOLVED` — fijo, no editable por el tenant), `label` (visible, editable), `is_terminal` (booleano: si el código representa un estado de cierre), `active`.

### 4.14 WorkOrderType

Campos: `id`, `tenant_id`, `code`, `label`, `active`. Ejemplo de `code`: `CORRECTIVE`, `PREVENTIVE`, `INSTALLATION`, `REVIEW`, `INSPECTION`, `WARRANTY`.

### 4.15 Priority

Campos: `id`, `tenant_id`, `code` (`LOW`, `NORMAL`, `HIGH`, `URGENT`), `label`, `sort_order`, `active`.

### 4.16 WorkOrderPhoto

Campos: `id`, `tenant_id`, `work_order_id` (FK), `storage_key` (ruta local en BOOTSTRAP / clave de Object Storage en producción), `caption` (opcional), `taken_at`, `uploaded_by`, `created_at`.

La base nunca almacena el binario, solo la referencia (`arquitectura.md` §7).

### 4.17 WorkOrderHistory

Registro de auditoría de eventos relevantes de una OT: cambios de estado, asignación/reasignación de técnico, reapertura.

Campos: `id`, `tenant_id`, `work_order_id` (FK), `event_type` (`STATUS_CHANGE`, `ASSIGNED`, `REOPENED`, ...), `previous_value`, `new_value`, `performed_by` (User), `performed_at`, `notes` (opcional, p. ej. motivo de reapertura).

Es la fuente de verdad de trazabilidad de la OT; no se sobreescribe ni se borra.

### 4.18 Notification

Campos: `id`, `tenant_id`, `work_order_id` (FK, opcional), `channel` (`EMAIL` en el MVP), `recipient`, `status` (`PENDING`, `SENT`, `FAILED`), `sent_at`, `created_at`.

### 4.19 SyncOperation

Cola de operaciones generadas offline por un `Technician`, conforme a `arquitectura.md` §8.

Campos: `id`, `tenant_id`, `user_id` (quién generó la operación), `entity_type` (`WORK_ORDER`, `WORK_ORDER_PHOTO`, ...), `entity_local_id` (id generado en el cliente), `entity_id` (id definitivo una vez aplicado, si corresponde), `operation_type` (`CREATE`, `UPDATE`), `payload` (JSON), `status` (`PENDING`, `SYNCED`, `ERROR`), `client_generated_at`, `synced_at`, `error_message` (opcional).

Restricción: procesamiento idempotente — reenviar la misma `SyncOperation` (mismo `entity_local_id` + `operation_type`) no debe duplicar el efecto.

---

## 5. Criterios de aislamiento multitenant

* Toda tabla de negocio listada en la sección 2 lleva `tenant_id` no nulo (excepto `Role`, catálogo de plataforma, y `User` de `PLATFORM_OWNER`).
* Ninguna FK puede apuntar a una fila de distinto `tenant_id`: se valida explícitamente en la capa de negocio de `apps/api` al crear o actualizar relaciones (`arquitectura.md` §3.3), independientemente de que la base de datos no lo garantice por sí sola en SQLite.
* Toda consulta de lectura sobre estas tablas exige `tenant_id` de contexto como condición — no existe una ruta de acceso a estas tablas que lo omita.
* `Person`, `PersonIdentification`, `Customer` y `Technician` no son la excepción: ninguna especialización puede referenciar una `Person` de otro tenant, y la búsqueda por identificación (§10.4) siempre se acota al `tenant_id` de contexto.
* Debe existir un test automatizado de aislamiento (`arquitectura.md` §3.5) que cubra al menos: Person, Customer, Technician, Location, Asset, WorkOrder.

---

## 6. Estrategia SQLite ↔ PostgreSQL

* Un único conjunto de modelos SQLAlchemy y un único historial de migraciones Alembic sirve a ambos motores.
* Tipos elegidos por compatibilidad (sección 1): sin funciones o tipos exclusivos de SQLite.
* `id` en UUID desde el inicio, aunque SQLite lo almacene como `TEXT`, para evitar recodificar claves al migrar.
* Los catálogos parametrizables (`WorkOrderStatus`, `Priority`, `WorkOrderType`, `AssetType`) se provisionan copiando el contenido de una `ConfigTemplate` al crear un `Tenant` (ver §9), mediante lógica de aplicación (no mediante datos fijos en migración de negocio), para que el comportamiento sea idéntico en ambos entornos.

---

## 7. Criterios futuros para RLS (PostgreSQL, producción)

Cuando se active RLS (`arquitectura.md` §3.4 y ROADMAP etapa 10):

* Política por tabla de negocio: `USING (tenant_id = current_setting('app.tenant_id')::uuid)`.
* La conexión de la API setea `app.tenant_id` al inicio de cada request autenticada, a partir del `tenant_id` ya resuelto en la capa de aplicación (nunca a partir de un valor enviado por el cliente).
* RLS actúa como defensa adicional, no reemplaza el filtrado explícito por `tenant_id` ya presente en la capa de negocio.
* Las tablas de plataforma (`Tenant`, `Role`) quedan fuera de esta política, ya que no pertenecen a un tenant o son compartidas.

---

## 8. Fuera de este modelo (ver PRD §58 y arquitectura.md §12)

No se modelan en esta versión: inventario/stock real con movimientos, facturación, cobranzas, contratos, presupuestos, ni un agrupador explícito de "visita" que contenga múltiples OT. Su incorporación futura no debe requerir alterar las relaciones aquí definidas, solo extenderlas.

---

## 9. Plantillas de configuración inicial (`ConfigTemplate`)

### 9.1 Propósito

Evitar que un tenant nuevo quede con catálogos vacíos. Al crear un `Tenant`, el sistema copia automáticamente a su configuración propia (`Priority`, `WorkOrderType`, `WorkOrderStatus`, `AssetType`) el contenido de una plantilla de configuración de plataforma.

No se usa un tenant ficticio como plantilla ni se reservan rangos artificiales de `tenant_id`: la plantilla es un conjunto de entidades propio, sin `tenant_id`, análogo a `Role` (catálogo de plataforma). Todo `Tenant` real sigue naciendo con UUID sin excepción.

### 9.2 Entidades

```text
ConfigTemplate
 │
 ├── TemplatePriority
 ├── TemplateWorkOrderType
 ├── TemplateWorkOrderStatus
 └── TemplateAssetType
```

* **ConfigTemplate**: `id` (UUID), `code` (único, estable — p. ej. `DEFAULT`), `name` (etiqueta visible para administración de plataforma), `active`.
* **TemplatePriority**: `id`, `template_id` (FK), `code`, `label`, `sort_order`.
* **TemplateWorkOrderType**: `id`, `template_id` (FK), `code`, `label`.
* **TemplateWorkOrderStatus**: `id`, `template_id` (FK), `code`, `label`, `is_terminal`. El `code` replica la misma semántica interna fija del núcleo (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `UNRESOLVED` — PRD §29): la plantilla no introduce códigos adicionales.
* **TemplateAssetType**: `id`, `template_id` (FK), `code`, `label`.

Cada tabla `Template*` mantiene una restricción `UNIQUE(template_id, code)`, análoga a la de su equivalente por tenant.

### 9.3 Provisionamiento de un tenant nuevo

Al crear un `Tenant`, `app.core.provisioning.provision_tenant_from_template(db, tenant_id, template_code="DEFAULT")`:

1. localiza la `ConfigTemplate` activa por `code` (`DEFAULT` en el MVP);
2. para cada catálogo (`Priority`, `WorkOrderType`, `WorkOrderStatus`, `AssetType`), copia una fila nueva por cada fila de la plantilla cuyo `code` el tenant todavía no tenga.

La copia crea filas físicamente propias del tenant (nuevo `id`, `tenant_id` propio) — nunca una referencia a la fila de la plantilla. A partir de ahí, personalizar `label`, `active` o `sort_order` en un tenant no modifica ni la plantilla ni ningún otro tenant (§5).

**Idempotencia:** el paso 2 compara contra los `code` que el tenant ya tiene antes de insertar. Reejecutar el provisionamiento sobre un tenant ya inicializado no duplica filas. La plantilla en sí es de solo lectura desde este proceso: nunca se escribe en `ConfigTemplate` ni en las tablas `Template*` al provisionar un tenant.

### 9.4 Extensión futura: plantillas por rubro

El modelo admite agregar plantillas adicionales sin cambios estructurales — únicamente nuevas filas `ConfigTemplate` (con su propio `code`) y sus `Template*` asociadas, por ejemplo:

```text
DEFAULT
CLIMATIZACION
ASCENSORES
ALARMAS
```

No se implementan en el MVP (solo existe `DEFAULT`); queda para cuando la asignación de plantilla por rubro sea una necesidad real del producto, por ejemplo asociando el `code` de la plantilla elegida al crear el `Tenant`.

---

## 10. Person y especializaciones de negocio

### 10.1 Propósito

Evitar que una misma persona real quede duplicada cuando participa con más de una función dentro de la misma empresa. Ejemplo: José Pérez puede ser simultáneamente Cliente y Técnico de un mismo tenant; debe existir una única `Person` y dos especializaciones (`Customer`, `Technician`) asociadas a ella, no dos registros independientes con los mismos datos generales repetidos.

### 10.2 Person: base común

`Person` (§4.5) concentra los datos generales de una persona física o jurídica: tipo de persona, nombre/razón social, dirección, teléfono, email, estado. Estos datos existen **una sola vez** por tenant y por persona. Ninguna especialización los repite.

Clave primaria conceptual: `(tenant_id, id)`, donde `id` es el `person_id` que referencian las especializaciones.

### 10.3 Especializaciones actuales y futuras

`Customer` (§4.7) y `Technician` (§4.8) son subtipos de `Person`: cada uno tiene clave `(tenant_id, person_id)`, que es a la vez su PK y una FK hacia `Person(tenant_id, id)` — relación `Person (1) ──── (0..1) Customer/Technician`. Solo contienen los atributos propios de esa función; nunca duplican nombre, dirección, teléfono ni email.

El patrón está preparado para agregar especializaciones futuras sin modificar `Person` ni las especializaciones existentes — basta con una tabla nueva con el mismo patrón de clave `(tenant_id, person_id)`:

```text
Person
 │
 ├── Customer      (implementado)
 ├── Technician     (implementado)
 ├── Supplier       (futuro, no implementado)
 ├── Partner        (futuro, no implementado — "Socio")
 ├── Renter         (futuro, no implementado — "Inquilino"; NO confundir con
 │                   el `Tenant` de la plataforma SaaS, que es la empresa
 │                   cliente de gi-ot — son dos conceptos homónimos distintos)
 ├── Owner          (futuro, no implementado — "Propietario")
 └── Fiduciary      (futuro, no implementado — "Fiduciario")
```

Ninguna de estas especializaciones futuras se implementa en el MVP; solo se documenta el patrón.

### 10.4 PersonIdentification y prevención de duplicados

`PersonIdentification` (§4.6) permite múltiples identificaciones por persona (p. ej. DNI y CUIT en Argentina) sin atar el modelo a un país: `country_code` + `identification_type` son campos abiertos, internacionalizables.

**Nivel obligatorio:** `UNIQUE(tenant_id, country_code, identification_type, identification_value)` impide registrar dos veces la misma identificación exacta dentro de un tenant. Al dar de alta una Persona, el backend busca primero por esta combinación dentro del tenant; si existe, se reutiliza la `Person` en lugar de crear una nueva (§10.6).

**Evolución futura (no implementada):** detección de duplicados débiles por coincidencia aproximada de nombre, email o teléfono, para sugerir (no forzar) una posible fusión. Queda documentada como posibilidad, sin heurística ni endpoint en el MVP.

### 10.5 Alta transparente desde la interfaz

El usuario nunca opera directamente sobre `Person`: interactúa con conceptos de negocio (`Clientes → Nuevo Cliente`, `Técnicos → Nuevo Técnico`). El backend resuelve internamente la existencia o creación de la `Person` subyacente.

Flujo de alta (igual para Customer y Technician, cambiando solo la especialización creada al final):

```text
Usuario completa: tipo de persona, país, tipo de identificación, número
        ↓
Backend busca Person por (tenant_id, country_code, identification_type, identification_value)
        ↓
   ¿Existe?
   ├── NO → crea Person + PersonIdentification + Customer|Technician
   │        en una única operación transaccional (§10.6);
   │        el usuario lo percibe como "Crear cliente" / "Crear técnico"
   │
   └── SÍ → informa que la Persona ya existe;
            recupera y muestra sus datos generales (editables);
            si ya tiene la especialización solicitada: informa que ya está
            registrada, no duplica nada;
            si no la tiene: crea únicamente Customer|Technician,
            reutilizando la Person existente
```

### 10.6 Transaccionalidad

La creación de `Person + PersonIdentification + Customer` (o `Technician`) es una única operación transaccional: si cualquier parte falla, no debe persistir ningún registro parcial. Igual criterio aplica cuando solo se agrega una especialización a una `Person` ya existente.

### 10.7 Actualización de datos comunes

Los datos generales (nombre, dirección, teléfono, email, tipo de persona, estado) se editan únicamente sobre `Person`, sin importar desde qué pantalla de especialización se originó la edición. Si se modifican desde la ficha de Técnico, el cambio queda en `Person` y es visible de inmediato al consultar esa misma persona como Cliente (y viceversa) — nunca hay una copia desactualizada en otra tabla.

### 10.8 Multitenancy

`Person`, `PersonIdentification`, `Customer` y `Technician` llevan `tenant_id` como el resto de las entidades de negocio (§5). No puede existir una especialización que referencie una `Person` de otro tenant, ni una identificación repetida entre tenants distintos — la unicidad de `PersonIdentification` está acotada por tenant, de modo que dos tenants pueden legítimamente registrar la misma identificación (p. ej. el mismo DNI) sin que eso implique relación alguna entre ambos.

### 10.9 Diferencia con roles de seguridad (RBAC)

Las especializaciones de negocio (`Customer`, `Technician`, y futuras `Supplier`/`Partner`/etc.) son un concepto independiente de los roles RBAC (`PLATFORM_OWNER`, `TENANT_ADMIN`, `TENANT_OFFICE`, `TENANT_TECHNICIAN`, modelo-datos.md §4.4). Una `Person` puede ser `Technician` sin tener nunca un `User` de acceso al sistema. Un `User` con permisos administrativos no necesita ser `Technician`. Ambos conceptos pueden coincidir en la práctica (un técnico de campo normalmente tiene un `User` con rol `TENANT_TECHNICIAN`), pero el modelo no fuerza ni infiere esa relación automáticamente.

### 10.10 Compatibilidad SQLite ↔ PostgreSQL

La clave compuesta `(tenant_id, person_id)` de las especializaciones y la FK compuesta hacia `Person(tenant_id, id)` se expresan con SQLAlchemy `ForeignKeyConstraint` de forma idéntica en ambos motores (§6); no dependen de ninguna función específica de SQLite ni de PostgreSQL.
