# AGENTS.md — gi-ot

## Propósito

Reglas permanentes y mínimas para cualquier agente que trabaje en `gi-ot`.

No duplicar aquí información disponible en documentos canónicos.

---

## Estado del proyecto

**Modo actual: BOOTSTRAP**

Objetivo:

Construir rápidamente un MVP vertical correcto antes de activar el circuito formal SDD / AI-NATIVE.

Durante BOOTSTRAP no ejecutar automáticamente:

* feature branches;
* worktrees;
* PR;
* Analyst / Reviewer / Builder / QA;
* auditorías formales;
* HITL por feature;
* `runs/<feature>/spec.md`.

La activación del circuito AI-NATIVE requiere decisión explícita del usuario.

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

6. `.agentic/`
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
* extensible.

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
* regresiones.

No perseguir cobertura artificial.

---

## Documentación

Actualizar el documento canónico correspondiente cuando cambie:

* producto;
* roadmap;
* stack;
* arquitectura;
* modelo de datos.

No duplicar información entre documentos.

---

## Evolución a SDD / AI-NATIVE

Evolución prevista:

`PRD → ROADMAP → BOOTSTRAP → MVP vertical → SDD → AI-NATIVE`

Cuando el usuario active AI-NATIVE:

1. reconciliar código, PRD y ROADMAP;
2. convertir pendientes en features;
3. utilizar `runs/<feature>/spec.md`;
4. activar las reglas de `.agentic/`;
5. aplicar auditoría, evidencias, HITL y Git según el template.

No reestructurar la aplicación para realizar esta transición.

---

## Git

Durante BOOTSTRAP no inicializar ni modificar la estrategia Git sin instrucción explícita.

Cuando Git esté activo, los mensajes de commit serán en español.

---

## Criterio general

Ante varias alternativas válidas, priorizar:

1. seguridad multitenant;
2. simplicidad;
3. parametrización;
4. experiencia móvil;
5. funcionamiento offline;
6. mantenibilidad;
7. mínima complejidad innecesaria.
