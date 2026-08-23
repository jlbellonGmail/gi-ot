# ROADMAP — gi-ot

## Estado

**Modo actual: BOOTSTRAP**

Objetivo actual:

Construir rápidamente un MVP vertical SaaS multitenant que permita completar una Orden de Trabajo de punta a punta.

Evolución prevista:

`PRD → ROADMAP → BOOTSTRAP → MVP vertical → SDD → AI-NATIVE`

Durante BOOTSTRAP se prioriza velocidad, simplicidad y validación funcional sin activar todavía el circuito agéntico formal.

---

# 00 — Definición del producto

* [x] PRD v0.1.
* [x] Modelo funcional.
* [x] Flujos principales.
* [x] Modelo conceptual de datos.
* [x] Arquitectura técnica.
* [x] Wireframes principales.
* [x] Decisiones técnicas iniciales.

**Resultado esperado:** dejar cerrada la definición mínima necesaria para comenzar construcción.

---

# 01 — Fundación SaaS

* [x] Crear aplicación web/PWA.
* [x] Crear API.
* [x] Configurar persistencia local con SQLite.
* [x] Configurar SQLAlchemy.
* [x] Configurar Alembic.
* [x] Crear modelo Tenant.
* [x] Implementar autenticación.
* [x] Implementar resolución segura del tenant.
* [x] Implementar RBAC.
* [x] Crear rol `PLATFORM_OWNER`.
* [x] Crear rol `TENANT_ADMIN`.
* [x] Crear rol `TENANT_OFFICE`.
* [x] Crear rol `TENANT_TECHNICIAN`.
* [x] Implementar prueba de aislamiento entre tenants.

**Criterio:** aunque BOOTSTRAP utilice SQLite, el modelo deberá nacer multitenant y preparado para PostgreSQL.

---

# 02 — Parametrización

* [x] Configuración del tenant.
* [x] Datos comerciales.
* [x] Tipos de activos.
* [x] Estados de OT.
* [x] Prioridades.
* [x] Tipos de trabajo.
* [x] Etiquetas visibles básicas.
* [x] Seed inicial por tenant mediante plantilla de configuración (`ConfigTemplate` `DEFAULT`, ver `docs/tecnica/modelo-datos.md` §9): valores estándar copiados al crear el tenant; personalizables sin afectar a otros tenants ni a la plantilla; provisionamiento idempotente; modelo preparado para futuras plantillas por rubro.

**Criterio:** evitar valores rígidos por rubro o empresa cuando puedan resolverse mediante configuración.

---

# 03 — Maestros

**Modelo de datos:** Cliente y Técnico se implementan como especializaciones de una entidad base `Person` compartida (no como entidades independientes), para que una misma persona real con más de una función dentro del tenant nunca quede duplicada. Detalle completo: `docs/tecnica/modelo-datos.md` §10; decisión: `docs/producto/decisiones-producto.md` §16.

* [x] Personas (`Person`): datos generales, base común de Cliente y Técnico.
* [x] Identificaciones de Persona (`PersonIdentification`): múltiples por persona, únicas por tenant.
* [x] Especialización Cliente (`Customer`).
* [x] Especialización Técnico (`Technician`).
* [x] Alta transparente desde `Clientes → Nuevo Cliente` (el usuario no opera sobre `Person`).
* [x] Alta transparente desde `Técnicos → Nuevo Técnico` (el usuario no opera sobre `Person`).
* [x] Reutilización de una Persona existente por identificación (sin duplicar Person dentro del tenant).
* [x] Actualización de datos comunes en `Person`, visible desde cualquier especialización.
* [x] Ubicaciones.
* [x] Activos.
* [x] Relaciones Cliente → Ubicación → Activo.
* [x] Validación de pertenencia al tenant en todas las entidades (incluyendo `Person`, `PersonIdentification`, `Customer`, `Technician`).

No implementar todavía en esta etapa: Proveedor, Socio, Inquilino, Propietario, Fiduciario u otras especializaciones futuras de `Person` (dejar solo el patrón preparado).

---

# 04 — Núcleo de Órdenes de Trabajo

* [x] Crear OT.
* [x] Asignar técnico.
* [x] Consultar OT.
* [x] Iniciar OT.
* [x] Registrar trabajo.
* [x] Cambiar estado.
* [x] Terminar OT.
* [x] Historial.
* [x] Reapertura controlada.
* [x] Validar aislamiento multitenant en operaciones de OT.

---

# 05 — Primer MVP vertical

Completar y validar el circuito:

`Tenant → Usuario → Cliente → Ubicación → Activo → OT → Técnico → Ejecución → Cierre → Historial`

El MVP vertical debe demostrar que:

* [x] una empresa puede operar dentro de su tenant;
* [x] un administrativo puede crear y asignar una OT;
* [x] un técnico puede ejecutar y cerrar la OT;
* [x] la oficina puede consultar el resultado;
* [x] el activo conserva historial;
* [x] otro tenant no puede acceder a esos datos.

Cuando este circuito funcione correctamente existe el **primer MVP vertical**.

**Resultado:** circuito validado de punta a punta, tanto a nivel de API (suite automatizada `apps/api/tests/test_work_orders.py`, incluyendo aislamiento multitenant específico de OT) como en ejecución real contra un servidor de desarrollo vivo (creación de tenant, cliente, ubicación, activo, técnico y OT; asignación; inicio; registro de trabajo; cierre; consulta de historial; y verificación de que un segundo tenant recibe 404 al intentar leer u operar sobre la OT del primero). Frontend (`apps/web/src/app/dashboard/ot/`) implementa el flujo completo: alta de OT, listado con filtros, detalle con acciones según rol (asignar, iniciar, registrar avance, cerrar, reabrir) e historial.

Este punto constituye el hito recomendado para evaluar la activación progresiva de SDD.

---

# 06 — Mobile / PWA

* [x] Interfaz mobile-first.
* [x] Instalación PWA.
* [x] Cámara.
* [x] Fotografías.
* [x] Lectura QR.
* [x] OT urgente.
* [x] Validación de experiencia real desde celular.

---

# 07 — Offline y sincronización

Preferentemente ejecutar esta etapa mediante SDD si el circuito AI-NATIVE ya fue activado.

* [ ] Datos disponibles localmente.
* [ ] IndexedDB.
* [ ] Cache Storage.
* [ ] Service Worker.
* [ ] Cola de operaciones pendientes.
* [ ] Trabajo sin conexión.
* [ ] Sincronización automática.
* [ ] Reintentos.
* [ ] Estado visible de sincronización.
* [ ] Manejo básico de conflictos.
* [ ] Fotografías pendientes de sincronización.
* [ ] Pruebas de recuperación después de pérdida de conectividad.

---

# 08 — Oficina

* [ ] Panel principal.
* [ ] Filtros.
* [ ] Búsqueda.
* [ ] Seguimiento de OT.
* [ ] Historial por cliente.
* [ ] Historial por activo.
* [ ] Visualización clara de estados y prioridades parametrizadas.
* [ ] Interfaz mobile-first para el panel de Oficina/Admin (hoy `apps/web/src/app/dashboard/*` es un shell de escritorio: el menú superior no entra en pantallas angostas). Detectado en validación real desde celular, ROADMAP §06.
* [ ] Sistema de tema claro/oscuro real (tokens de color), en vez de estilos hardcodeados por página. Sin esto, el modo oscuro automático de algunos navegadores rompe la legibilidad (ver caso detectado en §06).
* [ ] Revisión de diseño/UX de las pantallas mobile del técnico (`apps/web/src/app/tecnico/*`): hoy son funcionales pero visualmente mínimas, falta una pasada real de diseño.

---

# 09 — Comprobantes y comunicaciones

* [ ] Generar comprobante de OT.
* [ ] Branding básico por tenant.
* [ ] Envío por email.
* [ ] Evaluar WhatsApp según decisión técnica y comercial.

WhatsApp no deberá bloquear la disponibilidad del MVP inicial.

---

# 10 — Validación PostgreSQL

Antes de considerar el producto apto para producción:

* [ ] Levantar entorno PostgreSQL de validación.
* [ ] Ejecutar migraciones Alembic sobre PostgreSQL.
* [ ] Verificar compatibilidad SQLite → PostgreSQL.
* [ ] Ejecutar tests funcionales críticos.
* [ ] Ejecutar tests de aislamiento multitenant.
* [ ] Implementar y validar Row-Level Security.
* [ ] Verificar índices y restricciones.
* [ ] Validar almacenamiento externo de archivos.
* [ ] Corregir incompatibilidades detectadas.

**Criterio:** el paso SQLite → PostgreSQL debe ser una evolución de infraestructura, no una reescritura del producto.

---

# 11 — Piloto MVP

* [ ] Crear empresa piloto.
* [ ] Crear usuarios reales.
* [ ] Crear técnicos reales.
* [ ] Configurar parámetros del tenant.
* [ ] Ejecutar pruebas desde celular.
* [ ] Ejecutar pruebas sin conexión.
* [ ] Validar aislamiento entre tenants.
* [ ] Validar comportamiento sobre PostgreSQL.
* [ ] Corregir problemas UX.
* [ ] Validar circuito completo.
* [ ] Recoger observaciones del piloto.

---

# 12 — Activación AI-NATIVE / SDD

La activación será una decisión explícita del usuario.

* [ ] Declarar cierre de BOOTSTRAP.
* [ ] Reconciliar PRD, ROADMAP, documentación y código.
* [ ] Inicializar o normalizar Git.
* [ ] Definir línea base del proyecto.
* [ ] Incorporar la infraestructura AI-NATIVE del template.
* [ ] Convertir trabajo pendiente en features SDD.
* [ ] Crear especificaciones en `runs/<feature>/spec.md`.
* [ ] Activar Claude/Codex/OpenCode.
* [ ] Activar Analyst.
* [ ] Activar Reviewer.
* [ ] Activar Builder.
* [ ] Activar QA.
* [ ] Activar evidencias en `runs/`.
* [ ] Activar HITL.
* [ ] Activar estrategia de ramas y worktrees.
* [ ] Activar CI/CD.

La activación AI-NATIVE no debe requerir reestructurar ni reescribir la aplicación.

---

# 13 — Producción SaaS

* [ ] Desplegar frontend/PWA.
* [ ] Desplegar API.
* [ ] Provisionar PostgreSQL administrado.
* [ ] Provisionar Object Storage.
* [ ] Configurar variables y secretos.
* [ ] Configurar HTTPS.
* [ ] Configurar backups.
* [ ] Configurar logging y monitoreo básico.
* [ ] Validar RLS en producción.
* [ ] Validar aislamiento entre tenants.
* [ ] Validar recuperación ante errores.
* [ ] Publicar primera versión operativa.

---

# Evolución del ROADMAP

El ROADMAP no será reemplazado al activar SDD.

Durante BOOTSTRAP contiene objetivos funcionales relativamente amplios.

Al activar SDD, los trabajos pendientes evolucionarán a:

**features especificadas, construibles, auditables y verificables.**

Ejemplo:

```text
Antes:

[ ] Offline y sincronización

Después:

[ ] 20-persistencia-offline
[ ] 21-cola-sincronizacion
[ ] 22-resolucion-conflictos
[ ] 23-sincronizacion-fotografias
```

Cada feature podrá disponer de su especificación correspondiente en:

`runs/<feature>/spec.md`

---

# Fuentes relacionadas

Producto y alcance:

`docs/producto/PRD.md`

Stack tecnológico:

`docs/tecnica/stack.md`

Arquitectura, una vez definida:

`docs/tecnica/arquitectura.md`

Modelo de datos, una vez definido:

`docs/tecnica/modelo-datos.md`

---

# Regla de avance

No incorporar funcionalidades fuera del PRD simplemente porque resulten técnicamente atractivas.

Priorizar siempre el camino más corto que permita alcanzar:

**un MVP SaaS multitenant realmente utilizable de punta a punta.**
