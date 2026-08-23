# AGENTS.md — gi-ot

## Propósito

Reglas permanentes y mínimas para cualquier agente que trabaje en `gi-ot`.

No duplicar aquí información disponible en documentos canónicos.

---

## Estado del proyecto

**Modo actual: BOOTSTRAP**

Objetivo:

Construir rápidamente un MVP vertical correcto y evolucionarlo de forma controlada antes de activar el circuito formal SDD / AI-NATIVE.

El repositorio Git ya está activo.

La rama de integración durante BOOTSTRAP es:

`develop`

Durante BOOTSTRAP no ejecutar automáticamente:

* feature branches;
* worktrees;
* Pull Requests;
* Analyst / Reviewer / Builder / QA;
* auditorías formales;
* HITL por feature;
* `runs/<feature>/spec.md`.

La activación del circuito AI-NATIVE requiere decisión explícita del usuario.

Git puede utilizarse durante BOOTSTRAP para conservar una línea base limpia y trazable sin activar todavía el circuito agéntico completo.

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
   Reglas del circuito formal cuando AI-NATIVE esté activo.

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

Durante el MVP:

* frontend/PWA en `apps/web/`;
* API en `apps/api/`;
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

## Evolución a SDD / AI-NATIVE

Evolución prevista:

`PRD → ROADMAP → BOOTSTRAP → MVP vertical → SDD → AI-NATIVE`

Cuando el usuario active AI-NATIVE:

1. reconciliar código, PRD, ROADMAP y documentación;
2. convertir pendientes en features o milestones;
3. utilizar `runs/<feature>/spec.md`;
4. activar las reglas de `.agentic/`;
5. aplicar Analyst, Reviewer, Builder, QA y Code Reviewer según el template;
6. aplicar auditoría y evidencias;
7. ejecutar HITL;
8. activar estrategia formal de ramas, worktrees y PR;
9. activar CI/CD según corresponda.

Toda SPEC que afecte frontend deberá leer y respetar:

`docs/ui-ux/UI-UX-STANDARDS.md`

La SPEC documentará solamente comportamiento específico de la feature y excepciones justificadas.

No duplicará el estándar UI/UX transversal.

No reestructurar la aplicación únicamente para realizar esta transición.

---

## Git

Git está activo durante BOOTSTRAP.

Rama de integración:

`develop`

Reglas actuales:

* mantener `develop` como línea de trabajo e integración;
* no trabajar directamente sobre `main`;
* no crear feature branches, worktrees o PR automáticamente mientras AI-NATIVE no esté activo;
* no hacer commit ni push sin instrucción explícita del usuario;
* cuando el usuario solicite commit, incluir únicamente los cambios correspondientes al alcance aprobado;
* mensajes de commit en español;
* no utilizar `--force` salvo decisión humana explícita;
* no crear tags;
* no fusionar hacia `main` automáticamente.

Cuando el circuito AI-NATIVE sea activado, la estrategia Git formal del template reemplazará estas reglas operativas simplificadas.

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
