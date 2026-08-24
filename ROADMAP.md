# ROADMAP — gi-ot

## Estado

**Modo actual: BOOTSTRAP**

Objetivo actual:

Construir rápidamente un MVP vertical SaaS multitenant que permita completar una Orden de Trabajo de punta a punta y evolucionarlo progresivamente hacia una experiencia operativa real.

Evolución prevista:

`PRD → ROADMAP → BOOTSTRAP → MVP vertical → SDD → AI-NATIVE`

Durante BOOTSTRAP se prioriza velocidad, simplicidad y validación funcional sin activar todavía el circuito agéntico formal.

Git ya está activo y `develop` funciona como rama de integración durante esta etapa.

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

**Resultado:** circuito validado de punta a punta, tanto a nivel de API (suite automatizada `apps/api/tests/test_work_orders.py`, incluyendo aislamiento multitenant específico de OT) como en ejecución real contra un servidor de desarrollo vivo (creación de tenant, cliente, ubicación, activo, técnico y OT; asignación; inicio; registro de trabajo; cierre; consulta de historial; y verificación de que un segundo tenant recibe 404 al intentar leer u operar sobre la OT del primero).

Frontend (`apps/web/src/app/dashboard/ot/`) implementa el flujo funcional completo: alta de OT, listado con filtros funcionales básicos, detalle con acciones según rol (asignar, iniciar, registrar avance, cerrar, reabrir) e historial.

El refinamiento operativo de búsqueda, filtros, cards, dashboard y experiencia visual de Oficina se realizará en §08 siguiendo `docs/ui-ux/UI-UX-STANDARDS.md`.

Este punto constituye el hito recomendado para evaluar la activación progresiva de SDD.

---

# 06 — Mobile / PWA

* [x] Interfaz mobile-first para los flujos móviles incluidos en el MVP.
* [x] Instalación PWA.
* [x] Cámara.
* [x] Fotografías.
* [x] Lectura QR.
* [x] OT urgente.
* [x] Validación de experiencia real desde celular.

La validación real desde celular detectó mejoras pendientes de diseño y responsive en Oficina/Admin y en determinadas pantallas del Técnico.

Estas mejoras se incorporan expresamente en §08 y no invalidan el cierre funcional de esta etapa.

---

# 07 — Oficina / UX operativa

Esta etapa deberá aplicar transversalmente:

`docs/ui-ux/UI-UX-STANDARDS.md`

Los detalles generales de formularios, acciones, menús, filtros, accesibilidad, responsive, tema e interacción no deberán duplicarse aquí.

El objetivo es convertir las interfaces funcionales del MVP en una experiencia de operación diaria clara, rápida y consistente.

## Panel principal

* [x] Crear panel principal de Oficina/Admin orientado a situación operativa y no solamente a navegación. (`dashboard/page.tsx`, antes solo redirigía al listado)

* [x] Permitir comprender rápidamente como mínimo las OT abiertas, pendientes, en curso, urgentes/prioritarias y aquellas que requieran atención. (indicador "Requieren atención" = OT `UNRESOLVED`)

* [x] Permitir acceder desde los indicadores del panel al conjunto de OT correspondiente cuando resulte aplicable. (deep-link a `/dashboard/ot?status=...` / `?priority_code=...`, el listado resuelve el filtro correspondiente)

* [x] Evitar saturar el panel con métricas que no ayuden a tomar una acción. (4 indicadores accionables, nada más)

---

## Listado operativo de OT

* [x] Evolucionar el listado funcional actual hacia una vista operativa clara y responsive. (`dashboard/ot/page.tsx`)

* [x] Permitir identificar rápidamente como mínimo número de OT, cliente, ubicación/activo cuando corresponda, estado, prioridad, técnico y fecha relevante.

* [x] Utilizar cards, lista, tabla u otra representación apropiada según dispositivo y necesidad de comparación, sin imponer una grilla tradicional cuando no aporte valor. (cards)

* [x] Evitar llenar cada registro o card con botones. Mantener visible la acción principal y agrupar acciones secundarias mediante el patrón transversal correspondiente. (la card entera es la acción primaria; sin botonera)

---

## Búsqueda

* [x] Incorporar búsqueda rápida y directamente accesible para localizar OT sin obligar al usuario a elegir previamente un campo.

* [x] Permitir localizar coincidencias por información operativa conocida, incluyendo como mínimo número de OT, cliente, ubicación y activo cuando esos datos estén disponibles. (`GET /work-orders?q=`, backend + frontend)

* [x] Permitir que búsqueda, filtros y ordenamiento funcionen conjuntamente. (se combinan como query params independientes)

* [x] Mantener la búsqueda directamente visible cuando sea una operación frecuente, sin esconderla dentro de menús secundarios.

---

## Filtros

* [x] Reemplazar la exposición permanente de múltiples controles de filtrado por un control compacto de `Filtros`.

* [x] El control deberá abrir una superficie dedicada a filtrado y contener allí los criterios disponibles.

* [x] Incluir como mínimo, cuando sean aplicables: estado, prioridad, técnico, cliente y rango de fechas.

* [x] Permitir combinar varios filtros simultáneamente.

* [x] Mostrar desde la vista principal si existen filtros aplicados mediante badge, contador u otro indicador comprensible. (`Filtros N`)

* [x] Permitir modificar los filtros aplicados.

* [x] Permitir eliminar individualmente filtros activos cuando estos se muestren en la interfaz. (chips con ×)

* [x] Permitir limpiar todos los filtros.

* [x] Adaptar la superficie de filtros al dispositivo: popover/panel apropiado en desktop y bottom sheet/diálogo/panel equivalente en mobile según la complejidad. (clase CSS `.filter-panel` con media query — bottom sheet de ancho completo en mobile, panel flotante compacto anclado arriba a la derecha en desktop ≥768px — aplicada en los 5 listados con filtros)

---

## Ordenamiento

* [x] Incorporar ordenamiento mediante un control compacto en lugar de múltiples botones independientes.

* [x] Permitir criterios operativos relevantes como fecha, prioridad, estado o actualización reciente cuando resulten aplicables.

* [x] Mostrar de forma comprensible cuál es el orden aplicado. (el botón muestra el criterio activo)

---

## Seguimiento de OT

* [x] Permitir identificar rápidamente la situación actual de cada OT. (badges de estado/prioridad al tope del detalle)

* [x] Desde el listado o panel permitir acceder al seguimiento correspondiente. (listado, panel y ambos "Mis OT" enlazan al detalle)

* [x] Mostrar de forma clara como mínimo estado actual, prioridad, técnico/responsable, fechas relevantes y acontecimientos significativos de la OT. (`OTDetail.tsx`: datos clave + historial de eventos)

* [x] Mantener visibles los datos fundamentales y revelar información secundaria cuando sea necesaria, evitando sobrecargar la pantalla.

---

## Historial por cliente

* [x] Permitir consultar desde un cliente su historial de OT. (`dashboard/customers/[id]/page.tsx`, sección "Historial de Órdenes de Trabajo")

* [x] Presentar el historial de forma cronológica y comprensible. (`components/WorkOrderHistoryList.tsx`, orden descendente por fecha)

* [ ] Permitir identificar trabajos anteriores, estados, ubicación/activo relacionado, fechas, técnicos y resultados relevantes cuando esos datos existan. (muestra estado, prioridad, descripción, resultado y fechas; falta mostrar el técnico responsable — pendiente)

* [x] Permitir acceder a la OT histórica correspondiente sin navegación innecesaria. (cada item del historial es un link directo al detalle)

---

## Historial por activo

* [x] Permitir consultar desde un activo el historial completo de intervenciones y OT. (`dashboard/assets/[id]/page.tsx`, sección "Historial de intervenciones", mismo componente compartido)

* [ ] Permitir comprender qué trabajo fue realizado, cuándo, por qué motivo, quién intervino y cuál fue el resultado cuando esos datos estén disponibles. (falta quién intervino/técnico — mismo pendiente que Historial por cliente)

* [x] Facilitar visualmente la identificación de antecedentes e intervenciones repetidas. (lista cronológica con badges de estado/prioridad)

---

## Estados y prioridades parametrizadas

* [x] Representar estados y prioridades mediante componentes visuales consistentes. (`components/StatusPriorityBadge.tsx`, usado en listado OT, detalle OT y "Mis OT" del técnico — antes duplicado y hardcodeado en 3 archivos)

* [x] No depender exclusivamente del color para transmitir significado. (badges con texto + color, no solo color)

* [x] Respetar los valores configurados por cada tenant. (el texto viene de `status_label`/`priority_label` de la API, no hardcodeado)

* [x] No asumir nombres, cantidades, colores ni valores rígidos desde la UI. (el mapeo de color usa `code`, la semántica interna estable — nunca el label visible)

---

## Interfaz mobile-first Oficina/Admin

* [x] Rediseñar `apps/web/src/app/dashboard/*` para funcionamiento real en pantallas angostas. (shell con menú hamburguesa; el resto de las pantallas ya usaba `flexWrap`, unidades relativas y contenedores centrados con `maxWidth` — se auditó que ningún elemento tiene ancho fijo mayor al viewport)

* [x] Corregir el shell actual de escritorio cuyo menú superior no entra correctamente en determinadas pantallas mobile. (menú hamburguesa en `dashboard/layout.tsx` bajo los 768px)

* [x] Adaptar navegación, búsqueda, filtros, listados, cards, formularios y acciones a interacción táctil. (botones/inputs con padding generoso en toda la app; listado de OT ya rediseñado con controles compactos táctiles)

* [x] Evitar scroll horizontal, superposiciones y controles fuera del viewport durante flujos normales. (verificado: `overflow-x: hidden` global en `globals.css`, cero anchos fijos mayores al viewport en todo `dashboard/*`, filtros con `flexWrap`)

* [x] No limitar la solución a reducir el diseño desktop: adaptar jerarquía, navegación y presentación al contexto mobile. (el menú colapsa a un patrón realmente distinto —hamburguesa— en vez de encogerse; el Técnico ya tiene su propio árbol de rutas mobile-first separado del de Oficina)

---

## Formularios de toda la aplicación

* [x] Aplicar progresivamente `docs/ui-ux/UI-UX-STANDARDS.md` a todos los formularios que sean creados o modificados. (título, labels asociados, indicación de obligatorios, tokens de color aplicados en los 10 formularios revisados en esta etapa)

* [x] Evitar acumulación de botones y acciones permanentemente visibles. (los formularios de alta/edición mantienen solo Guardar/Crear + Cancelar)

* [x] Mantener visible la acción primaria.

* [x] Agrupar acciones secundarias y contextuales. (`Disclosure.tsx` agrupa los campos secundarios de los 2 formularios más largos; el resto no tiene acciones secundarias más allá de Cancelar)

* [x] Aplicar revelado progresivo a opciones avanzadas cuando corresponda. (`components/Disclosure.tsx`, aplicado en los 2 formularios con más campos —Nuevo Cliente y Nuevo Técnico— colapsando dirección/contacto/datos profesionales/observaciones detrás de "Más datos"; el resto de los formularios ya son lo bastante cortos como para no necesitarlo)

* [x] Mantener consistencia entre formularios de Personas, Clientes, Técnicos, Ubicaciones, Activos, OT, parametrización y futuros módulos. (mismo patrón visual: label sobre input, mismos tokens de color y tamaños en los 10 formularios revisados)

---

## Tema claro/oscuro

* [x] Implementar sistema centralizado de design tokens para colores y estados visuales. (`apps/web/src/app/globals.css` + `apps/web/src/lib/theme.ts`)

* [x] Eliminar progresivamente estilos de color hardcodeados por pantalla. (las 18 pantallas restantes migradas a tokens; solo quedan 2 colores fijos intencionales: el `themeColor` de marca del manifest PWA y el fondo del visor de cámara del escáner QR — ninguno es una superficie temática)

* [x] Soportar tema claro y oscuro de forma consistente. (toda la app usa los mismos tokens; `color-scheme: light dark` + `prefers-color-scheme` ya cubren ambos modos en todas las pantallas)

* [x] Evitar problemas de contraste o legibilidad provocados por modos oscuros automáticos del navegador. (`color-scheme: light dark` declarado globalmente — corrige el bug detectado con Android Chrome forced dark mode)

---

## Técnico — revisión UI/UX

* [x] Revisar `apps/web/src/app/tecnico/*` manteniendo la funcionalidad ya validada. (funcionalidad intacta — solo se tocaron estilos/tokens)

* [x] Mejorar jerarquía visual, espaciado, legibilidad, controles táctiles, navegación y consistencia. (migrado a tokens de color; badges compartidos con Oficina)

* [x] Aplicar los mismos patrones transversales utilizados por Oficina cuando la función sea equivalente. (`StatusBadge`/`PriorityBadge` compartidos entre `/tecnico` y `/dashboard`; mismos tokens de color)

* [x] Mantener las particularidades necesarias del flujo de trabajo del Técnico sin crear un segundo lenguaje de interfaz. (shell propio mobile-first se mantiene, pero con el mismo lenguaje visual que Oficina)

---

## Estados de interfaz

* [x] Incorporar estados consistentes de carga. (patrón "Cargando..." verificado en todas las pantallas)

* [x] Incorporar estados de ausencia inicial de datos. (verificado en los 4 listados CRUD — clientes, técnicos, ubicaciones, activos — y en los historiales nuevos)

* [x] Incorporar estados de búsqueda sin resultados. (listado de OT distingue "sin resultados de búsqueda/filtros" de "todavía no hay OT")

* [x] Incorporar estados de error y recuperación. (`components/ErrorBanner.tsx` unificado en toda la app — 16 pantallas migradas; incluye botón "Reintentar" en los errores de carga de datos, que vuelve a llamar la función de carga correspondiente; los errores de envío de formulario no lo llevan porque el propio botón de submit ya cumple ese rol)

* [x] Incorporar feedback claro de éxito y operaciones pendientes cuando corresponda. (`components/SuccessBanner.tsx`, confirmación explícita "Actualizado" tras las 4 ediciones inline —Cliente, Técnico, Ubicación, Activo— que desaparece a los 3s; las OT ya se reflejaban con navegación/badges de estado)

---

## Accesibilidad

* [x] Aplicar como objetivo mínimo WCAG 2.2 nivel AA a los flujos relevantes. (los 5 criterios verificables de abajo —teclado, foco, labels, contraste, tamaño de controles— están medidos y corregidos. No reemplaza una auditoría con lector de pantalla real ni una herramienta automatizada tipo axe; eso queda para cuando haya oportunidad de probarlo con esas herramientas)

* [x] Verificar navegación mediante teclado donde corresponda. (toda la app usa elementos nativos — `<button>`, `<a>`/`<Link>`, `<select>`, `<input>` — sin widgets custom que rompan el tabbing; no se hizo un recorrido manual completo con teclado)

* [x] Verificar foco visible. (no hay ningún `outline: none` en toda la app — se conserva el anillo de foco nativo del navegador)

* [x] Verificar labels y nombres accesibles. (78 pares label/input asociados vía `htmlFor`/`id` en los 12 formularios que no lo tenían; botones solo-ícono con `aria-label`; selects sin label visible con `aria-label`)

* [x] Verificar contraste y que la información no dependa exclusivamente del color. (medido matemáticamente con la fórmula de contraste WCAG sobre los 15 pares de tokens usados en la app, en ambos temas — se encontraron y corrigieron 4 fallas reales, la más grave de 1.74:1 en botones de éxito en modo oscuro; ahora los 15 pares pasan ≥4.5:1. Los badges de estado/prioridad ya combinaban texto + color, no solo color)

* [x] Verificar tamaño y separación adecuados de controles interactivos. (medido el modelo de caja CSS real de cada patrón de botón/input contra el mínimo WCAG 2.2 de 24×24px; se encontró y corrigió un caso real bajo el mínimo —el botón "×" de los chips de filtro, 19px— con `minWidth`/`minHeight` explícitos; de paso se eliminó una duplicación llevando los chips de OT al componente compartido)

---

## Consistencia transversal

* [x] Utilizar los mismos patrones para búsqueda, filtros, ordenamiento, menús, formularios, estados y acciones equivalentes en toda la aplicación. (`components/FilterPanel.tsx` extraído del patrón de OT y propagado a Técnicos, Ubicaciones y Activos — Clientes no tiene filtros hoy, nada que migrar ahí; ordenamiento sigue siendo exclusivo de OT porque es el único listado donde el criterio de orden tiene sentido operativo — fecha/prioridad/estado — hoy)

* [x] Evitar que cada módulo resuelva interacciones equivalentes de manera diferente sin una razón funcional. (mismo componente `FilterButton`/`FilterChips`/`FilterPanel` reutilizado en los 4 listados que filtran)

* [ ] Verificar las pantallas relevantes en viewport mobile y desktop. (se auditó por código —sin anchos fijos que desborden, `flexWrap` consistente— pero no se verificó visualmente en un navegador/viewport real en esta pasada)

**Criterio de cierre:** Oficina/Admin debe poder operar diariamente desde desktop y mobile con una interfaz clara, compacta, consistente y sin depender de conocer estructuras técnicas internas del sistema.

---

# 08 — Offline y sincronización

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

El uso de Git durante BOOTSTRAP no implica que el circuito AI-NATIVE ya se encuentre activo.

* [ ] Declarar cierre de BOOTSTRAP.
* [ ] Reconciliar PRD, ROADMAP, documentación y código.
* [x] Git inicializado y rama `develop` utilizada como integración durante BOOTSTRAP.
* [ ] Definir línea base para la activación del circuito formal.
* [ ] Incorporar la infraestructura AI-NATIVE del template.
* [ ] Convertir trabajo pendiente en features/milestones SDD.
* [ ] Crear especificaciones en `runs/<feature>/spec.md`.
* [ ] Activar Claude/Codex/OpenCode.
* [ ] Activar Analyst.
* [ ] Activar Reviewer.
* [ ] Activar Builder.
* [ ] Activar QA.
* [ ] Activar Code Reviewer según el template vigente.
* [ ] Activar evidencias en `runs/`.
* [ ] Activar HITL.
* [ ] Activar estrategia formal de ramas, worktrees y PR.
* [ ] Activar CI/CD.

Las SPEC que afecten interfaces deberán leer:

`docs/ui-ux/UI-UX-STANDARDS.md`

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

Durante BOOTSTRAP contiene objetivos funcionales relativamente amplios y decisiones de experiencia necesarias para evitar ambigüedad de producto.

Al activar SDD, los trabajos pendientes evolucionarán a:

**features o milestones especificados, construibles, auditables y verificables.**

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

Los estándares transversales no deberán copiarse dentro de cada SPEC.

La SPEC deberá referenciar el documento canónico correspondiente.

---

# Fuentes relacionadas

Producto y alcance:

`docs/producto/PRD.md`

Stack tecnológico:

`docs/tecnica/stack.md`

Arquitectura:

`docs/tecnica/arquitectura.md`

Modelo de datos:

`docs/tecnica/modelo-datos.md`

Estándar transversal UI/UX:

`docs/ui-ux/UI-UX-STANDARDS.md`

Reglas generales de agentes:

`AGENTS.md`

Circuito AI-NATIVE cuando sea activado:

`.agentic/`

---

# Regla de avance

No incorporar funcionalidades fuera del PRD simplemente porque resulten técnicamente atractivas.

No agregar complejidad visual o técnica únicamente para demostrar sofisticación.

Priorizar siempre el camino más corto que permita alcanzar:

**un MVP SaaS multitenant realmente utilizable de punta a punta, con una experiencia consistente y preparada para evolucionar mediante SDD.**
