# AGENTS.md — gi-ot

## Propósito

Reglas permanentes y mínimas para cualquier agente que trabaje en `gi-ot`.

No duplicar aquí información disponible en documentos canónicos.

---

## Estado del proyecto

**Modo actual: AI-NATIVE v2** (adopción en curso en `feature/adopcion-template-v2`)

Histórico:
- Puntos 00–09 construidos bajo modo **BOOTSTRAP** (ver sección "Histórico BOOTSTRAP" abajo).
- La activación AI-NATIVE de agosto de 2026 es una transición legacy.
- A partir del merge de esta feature, todo trabajo nuevo utilizará el mecanismo v2 definido en `.agentic/`.

El repositorio Git ya está activo.

La rama de integración es:

`develop`

Durante AI-NATIVE se ejecutan obligatoriamente:

* feature branches (una por feature/milestone);
* Pull Requests hacia `develop`;
* Circuito v2: Planner → Builder → Reviewer, con QA y Code Review como gates;
* Auditorías formales y evidencias en `runs/<feature>/`;
* HITL (Human-In-The-Loop) antes de merge;
* `runs/<feature>/spec.md` como contrato inmutable;
* CI/CD automático en PR (GitHub Actions).

Git se utiliza con la estrategia formal definida en `.agentic/workflows/git.md`.

---

## Histórico BOOTSTRAP (Puntos 00–09)

Los puntos 00–09 fueron construidos en modo BOOTSTRAP para validar rápidamente un MVP vertical:

- **00** — Definición del producto (PRD, modelo funcional, arquitectura)
- **01** — Fundación SaaS (multitenancy, auth, RBAC, roles base)
- **02** — Parametrización (config templates, catálogos base)
- **03** — Maestros (Person, Customer, Technician, Ubicaciones, Activos)
- **04** — Núcleo OT (crear, asignar, ejecutar, cerrar, historial, reapertura)
- **05** — MVP vertical (circuito completo punta a punta validado)
- **06** — Mobile/PWA (mobile-first, cámara, QR, fotos, OT urgente)
- **07** — Oficina/UX operativa (dashboard, listados, búsqueda, filtros, formularios, tema, accesibilidad)
- **08** — Offline y sincronización (IndexedDB, Service Worker, cola, sync, conflictos, fotos)
- **09** — Comprobantes y comunicaciones (generación HTML/PDF, branding tenant, email SMTP, WhatsApp evaluado)

Este histórico **no se reescribe, rebasea ni reconstruye**. Sirve como contexto y línea base.

---

## Fuentes de verdad

Leer según la tarea:

1. `docs/producto/PRD.md`
   Producto, alcance y reglas funcionales.

2. `ROADMAP.md`
   Prioridades y orden de construcción.

3. `docs/tecnica/stack.md`
   Stack tecnológico aprobado.

4. `docs/tecnica/arquitectura.md`
   Arquitectura aprobada.

5. `docs/tecnica/modelo-datos.md`
   Persistencia y modelo de datos.

6. `docs/ui-ux/UI-UX-STANDARDS.md`
   Estándar transversal obligatorio para toda interfaz, formulario, listado, navegación e interacción visual.

7. `.agentic/`
   **Reglas del circuito formal AI-NATIVE (fuente canónica obligatoria).**

No duplicar contenido de estos documentos dentro de `AGENTS.md`.

---

## Principios obligatorios

`gi-ot` debe mantenerse:

* SaaS;
* multitenant;
* multirrubro;
* parametrizable;
* mobile-first;
* preparado para offline;
* simple;
* extensible;
* visualmente consistente;
* accesible.

No crear variantes del código por cliente.

La personalización debe resolverse primero mediante configuración.

---

## Multitenancy

El tenant es una frontera de seguridad.

Toda entidad de negocio debe pertenecer directa o indirectamente a un tenant.

Nunca asumir una única empresa.

Toda operación debe validar:

* identidad;
* tenant;
* permisos.

Nunca confiar en un `tenant_id` recibido desde el cliente sin validarlo contra la identidad autenticada.

Debe existir prueba automatizada de aislamiento entre tenants.

---

## Roles base

Roles iniciales:

* `PLATFORM_OWNER`
* `TENANT_ADMIN`
* `TENANT_OFFICE`
* `TENANT_TECHNICIAN`

Los nombres visibles podrán parametrizarse.

Las capacidades internas no deben depender del texto mostrado.

---

## Parametrización

Evitar valores de negocio rígidos cuando puedan variar por empresa o rubro.

Ejemplos:

* estados de OT;
* prioridades;
* tipos de activo;
* tipos de trabajo;
* motivos;
* etiquetas;
* branding;
* configuración de notificaciones.

Separar siempre:

**semántica interna estable**

de

**etiqueta visible configurable**.

La UI no debe asumir cantidades, nombres, colores o valores fijos cuando estos sean parametrizables por tenant.

---

## UI / UX

Toda pantalla o formulario nuevo, y toda modificación significativa de una interfaz existente, debe cumplir:

`docs/ui-ux/UI-UX-STANDARDS.md`

El estándar aplica transversalmente a:

* Oficina/Admin;
* Técnico;
* Personas;
* Clientes;
* Técnicos;
* Ubicaciones;
* Activos;
* Órdenes de Trabajo;
* Parametrización;
* configuración;
* futuros módulos.

Principios mínimos:

* mobile-first real;
* baja saturación visual;
* acciones primarias visibles;
* acciones secundarias agrupadas;
* búsqueda frecuente directamente accesible;
* filtros y opciones complejas bajo controles compactos;
* feedback visual de filtros, estados y operaciones activas;
* formularios consistentes;
* design tokens;
* tema claro/oscuro;
* accesibilidad;
* estados de carga, vacío, error y éxito;
* ausencia de scroll horizontal en flujos normales;
* consistencia entre desktop y mobile.

No llenar formularios, cabeceras, listados o cards con botones independientes cuando las acciones puedan organizarse mediante menú, popover, diálogo, drawer o equivalente.

No ocultar una acción primaria o extremadamente frecuente únicamente para reducir elementos visibles.

---

## Skills de diseño

Una Skill de frontend/UI puede utilizarse como herramienta auxiliar cuando la tarea afecte la experiencia visual.

La Skill:

* no sustituye el PRD;
* no sustituye el ROADMAP;
* no sustituye `UI-UX-STANDARDS.md`;
* no decide reglas funcionales;
* no puede introducir un nuevo design system por iniciativa propia;
* no puede cambiar el stack aprobado.

Si `frontend-design` u otra Skill equivalente está disponible, utilizarla solamente cuando aporte valor a tareas de diseño o implementación frontend.

No instalar, eliminar o cambiar Skills automáticamente sin instrucción explícita del usuario.

---

## Stack y arquitectura

No elegir tecnologías nuevas si el stack ya está definido en:

`docs/tecnica/stack.md`

No cambiar el stack sin decisión explícita.

Arquitectura actual:

* frontend/PWA en `apps/web/` (Next.js + React + TypeScript);
* API en `apps/api/` (FastAPI + SQLAlchemy + Alembic);
* monolito modular;
* evitar microservicios y complejidad prematura.

La PWA no accede directamente a las tablas.

Las reglas de negocio pasan por la API.

---

## Offline

Offline es un requisito funcional.

Toda funcionalidad móvil relevante debe considerar:

* datos disponibles localmente;
* operaciones pendientes;
* reintentos;
* sincronización;
* conflictos;
* estado visible de sincronización.

Nunca mostrar una operación como sincronizada si solo existe localmente.

---

## Seguridad

Nunca almacenar en el repositorio:

* contraseñas;
* secretos;
* tokens;
* credenciales reales.

Usar variables de entorno.

Preservar siempre aislamiento multitenant y autorización por rol.

---

## Tests

Priorizar tests sobre:

* multitenancy;
* permisos;
* reglas de negocio;
* operaciones críticas;
* sincronización;
* regresiones;
* flujos UI críticos cuando corresponda.

No perseguir cobertura artificial.

Las interfaces críticas deben verificarse al menos en viewport mobile y desktop.

---

## Documentación

Actualizar el documento canónico correspondiente cuando cambie:

* producto;
* roadmap;
* stack;
* arquitectura;
* modelo de datos;
* estándar UI/UX.

No duplicar información entre documentos.

Las SPEC futuras deben referenciar los documentos transversales en lugar de copiarlos.

---

## Circuito AI-NATIVE (fuente canónica: `.agentic/`)

### Roles y flujo obligatorio

Los roles conceptuales canónicos son Planner, Builder y Reviewer. Son
capacidades, no nombres de herramientas ni modelos.

```
ASSESS → Planner → Builder → validaciones → Reviewer → convergence → HITL → PR
```

Analyst, QA y Code Reviewer se conservan como aliases y responsabilidades
legacy: Analyst pasa a Planner; QA y Code Reviewer son gates/capacidades
consumidas por Reviewer. Las evidencias anteriores a v2 no se reinterpretan.

### Gates obligatorios

1. ASSESS determinístico y SDD proporcional: LIGHT, STANDARD o FULL.
2. Planner produce intención, alcance, riesgos y plan trazable.
3. Builder implementa sólo el contrato aprobado y produce evidencia.
4. Validaciones ejecutan tests, lint, typecheck, build y migraciones si aplican.
5. Reviewer verifica intención, resultado, seguridad, arquitectura, QA y código.
6. Convergence limita findings, iteraciones y presupuesto; falla de forma segura.
7. HITL humano autoriza MERGE o RELEASE; el agente no mergea por iniciativa propia.

### Git (AI-NATIVE)

Estrategia formal en `.agentic/workflows/git.md`:

- `main` — Solo releases (protegida)
- `develop` — Integración (protegida, solo PR)
- `feature/<nombre>` — Una por feature, desde `develop`
- `hotfix/<nombre>` — Solo correcciones críticas en `main`
- **Prohibido**: commit directo a `develop`/`main`, force push, merge sin PR, merge sin CI verde, merge sin HITL
- **Obligatorio**: squash merge, delete feature branch, mensajes en español

### CI/CD (GitHub Actions)

`.github/workflows/ci.yml` separa gates de gobernanza/lifecycle, tests de
producto y la validación PostgreSQL futura. La PR #2 de PostgreSQL no es
baseline ni dependencia de esta adopción.

### HITL

Proceso en `.agentic/hitl.md`:
- Pre-merge a develop (obligatorio)
- Pre-release a main (obligatorio)
- Decisiones irreversibles (arquitectura, migraciones destructivas)
- Registro inmutable en `runs/<feature>/hitl.md`

### Fuentes de verdad

Git/GitHub real prevalece sobre documentos derivados. `CONSTITUTION.md`
contiene principios; `AGENTS.md` reglas operativas; `ROADMAP.md` dirección;
el SDD contrato concreto; `SUMMARY.md` reentrada resumida; `runs/` evidencia;
`.audit/` auditoría independiente; `STATUS.md` observación derivada.

### Legacy

`runs/09-comprobantes/**` y `runs/activar-ai-native/**` son evidencia
`LEGACY EVIDENCE — PRE TEMPLATE V2`. Se preservan sin renombrar, mover,
recalificar ni completar retroactivamente.

---

## Criterio general

Ante varias alternativas válidas, priorizar:

1. seguridad multitenant;
2. simplicidad;
3. parametrización;
4. experiencia de usuario;
5. experiencia móvil;
6. funcionamiento offline;
7. accesibilidad;
8. consistencia visual;
9. mantenibilidad;
10. mínima complejidad innecesaria.
