# UI-UX-STANDARDS — gi-ot

## Propósito

Definir el estándar transversal de interfaz y experiencia de usuario de `gi-ot`.

Estas reglas aplican a toda la aplicación y deben evitar que cada feature, pantalla o agente invente patrones de interacción diferentes.

Este documento define principios y patrones.

Las reglas funcionales pertenecen al PRD, ROADMAP y SPEC correspondiente.

---

# 1 — Alcance

El estándar aplica a:

* Oficina/Admin;
* Técnico;
* Personas;
* Clientes;
* Técnicos;
* Ubicaciones;
* Activos;
* Órdenes de Trabajo;
* parametrización;
* configuración;
* formularios;
* listados;
* búsquedas;
* filtros;
* historiales;
* dashboards;
* futuras áreas de la aplicación.

Toda nueva interfaz deberá cumplir este documento.

Las interfaces existentes deberán evolucionar progresivamente hacia este estándar cuando sean modificadas.

---

# 2 — Principios generales

La experiencia debe ser:

* mobile-first;
* simple;
* limpia;
* rápida;
* coherente;
* predecible;
* accesible;
* orientada a la tarea;
* adecuada para operación frecuente.

La interfaz deberá privilegiar la información necesaria para trabajar y evitar ruido visual.

No confundir cantidad de controles visibles con facilidad de uso.

---

# 3 — Jerarquía de acciones

Toda pantalla deberá distinguir entre:

## Acción primaria

Es la acción principal de la tarea actual.

Ejemplos:

* Nueva OT;
* Guardar;
* Crear cliente;
* Asignar;
* Finalizar OT.

Debe ser fácilmente reconocible y normalmente permanecer visible.

No esconder acciones primarias dentro de un menú contextual solamente para limpiar visualmente la pantalla.

---

## Acciones frecuentes

Son acciones utilizadas repetidamente durante la operación.

Ejemplos:

* buscar;
* filtrar;
* ordenar;
* actualizar determinados estados.

Deben disponer de acceso rápido mediante controles claros y compactos.

---

## Acciones secundarias

Son operaciones válidas pero menos frecuentes.

Siempre que resulte apropiado deberán agruparse mediante:

* menú contextual;
* menú de overflow `⋯`;
* popover;
* menú equivalente.

Evitar crear numerosos botones independientes.

---

## Acciones avanzadas

Configuraciones u operaciones excepcionales deberán mostrarse solamente cuando sean solicitadas.

Podrán utilizar:

* popover;
* diálogo;
* drawer;
* panel;
* bottom sheet en mobile.

---

# 4 — Regla de limpieza visual

Como patrón general:

**acción visible → control compacto → superficie dedicada → opciones**

Ejemplos:

`Filtros → panel de filtros`

`Ordenar → opciones de orden`

`⋯ → acciones secundarias`

`Configuración → panel específico`

Una superficie dedicada deberá contener opciones relacionadas con una única finalidad.

No mezclar acciones conceptualmente diferentes dentro del mismo popup o menú.

---

# 5 — Formularios

Todos los formularios deberán seguir una estructura consistente.

Como mínimo:

* título claro;
* contexto de lo que se está creando o editando;
* campos agrupados lógicamente;
* labels visibles;
* indicación comprensible de campos obligatorios;
* validaciones próximas al campo afectado;
* mensajes de error accionables;
* acción primaria clara;
* acciones secundarias visualmente subordinadas.

Evitar formularios que presenten simultáneamente una cantidad excesiva de opciones.

Cuando existan datos avanzados o poco frecuentes, aplicar revelado progresivo mediante secciones o controles apropiados.

---

# 6 — Alta de entidades relacionadas

Cuando el usuario esté creando una entidad funcional no deberá verse obligado a comprender detalles internos del modelo de datos.

Ejemplo:

`Nuevo Cliente`

puede internamente crear o reutilizar:

`Person → Customer`

pero la experiencia deberá continuar siendo:

`Nuevo Cliente`

Cuando sea necesario detectar registros existentes, el sistema deberá ayudar al usuario mediante identificadores y coincidencias relevantes sin obligarlo a navegar previamente a otra entidad técnica.

---

# 7 — Acciones de formulario

Evitar barras cargadas de botones.

Como criterio general:

* acción primaria visible;
* cancelar/volver claramente disponible;
* acciones secundarias agrupadas cuando corresponda;
* acciones destructivas separadas de acciones normales.

En formularios extensos utilizados desde mobile podrá evaluarse mantener la acción primaria accesible durante el desplazamiento.

La decisión concreta dependerá de cada flujo.

---

# 8 — Acciones destructivas

Eliminar, descartar, cancelar definitivamente o ejecutar operaciones irreversibles debe diferenciarse de las acciones normales.

Cuando exista riesgo real de pérdida de información deberá existir confirmación apropiada.

No utilizar confirmaciones innecesarias para operaciones fácilmente reversibles.

Las acciones destructivas no deberán quedar inmediatamente junto a la acción primaria si existe riesgo de activación accidental.

---

# 9 — Búsqueda

Cuando buscar sea una operación frecuente, el buscador deberá permanecer directamente accesible.

No esconder un buscador de uso cotidiano dentro de menús secundarios únicamente para reducir elementos visibles.

El usuario debería poder buscar utilizando información que naturalmente conozca.

Ejemplos en OT:

* número;
* cliente;
* ubicación;
* activo;
* técnico;
* otros identificadores relevantes.

No obligar al usuario a seleccionar previamente el campo exacto salvo que exista una necesidad funcional concreta.

---

# 10 — Búsqueda y filtros

Búsqueda y filtros deberán poder trabajar simultáneamente.

Conceptualmente:

`resultado = búsqueda + filtros activos + ordenamiento`

Modificar uno de ellos no deberá eliminar silenciosamente los demás.

---

# 11 — Filtros

No presentar permanentemente todos los campos de filtrado ocupando espacio de la pantalla.

Utilizar un control compacto de filtros.

Ejemplo conceptual:

`[ Buscar... ] [ Filtros 2 ] [ Ordenar ]`

El control deberá abrir una superficie dedicada con las opciones disponibles.

Los filtros podrán incluir, según la entidad:

* estado;
* prioridad;
* técnico;
* cliente;
* fechas;
* tipo;
* ubicación;
* activo;
* otros criterios definidos por la feature.

---

# 12 — Estado de filtros

El usuario debe reconocer sin abrir el panel si existen filtros activos.

El control podrá utilizar:

* badge;
* contador;
* indicador visual;
* texto breve.

Ejemplo:

`Filtros 3`

No depender exclusivamente del color.

---

# 13 — Filtros activos

Cuando facilite la comprensión del resultado podrán mostrarse únicamente los filtros actualmente aplicados mediante chips o etiquetas compactas.

Ejemplo:

`Estado: Abierta ×`

`Prioridad: Urgente ×`

No mostrar todos los filtros disponibles permanentemente.

Debe poder:

* quitar un filtro individual;
* modificar filtros;
* limpiar todos.

---

# 14 — Superficie de filtros

En desktop podrá utilizarse:

* popover;
* popup contextual;
* drawer cuando las opciones necesiten más espacio.

En mobile podrá utilizarse:

* bottom sheet;
* diálogo;
* panel adaptado a pantalla pequeña.

La misma función no necesita utilizar exactamente el mismo contenedor visual en todos los dispositivos.

Debe conservar el mismo significado y comportamiento.

---

# 15 — Ordenamiento

No llenar la interfaz con botones independientes para cada criterio.

Utilizar un único control de ordenamiento cuando existan varias opciones.

Ejemplo:

`Ordenar`

podrá ofrecer:

* fecha;
* prioridad;
* estado;
* actualización reciente;
* otros criterios relevantes.

El usuario deberá poder reconocer el orden actualmente aplicado.

---

# 16 — Listados

La aplicación no está obligada a utilizar una grilla tradicional en todos los escenarios.

Elegir la representación que facilite mejor la tarea.

Podrán utilizarse:

* cards;
* listas;
* tablas;
* vistas compactas;
* combinaciones responsive.

La elección debe considerar:

* cantidad de información;
* comparación entre registros;
* frecuencia de uso;
* dispositivo;
* acciones disponibles.

---

# 17 — Mobile y desktop

En mobile priorizar:

* lectura vertical;
* controles táctiles;
* información esencial;
* cards o listas cuando resulten más apropiadas;
* acciones compactas;
* ausencia de scroll horizontal.

En desktop podrá aprovecharse el espacio adicional mediante:

* más columnas;
* mayor densidad informativa;
* tablas cuando favorezcan comparación;
* paneles contextuales.

Mobile no debe ser simplemente el desktop reducido.

---

# 18 — Cards

Cuando se utilicen cards, mostrar primero la información que permita identificar y decidir.

Una card de OT podrá priorizar:

* número de OT;
* cliente;
* activo o ubicación;
* estado;
* prioridad;
* técnico;
* fecha relevante.

No convertir cada card en una botonera.

La acción principal podrá permanecer visible.

Las acciones secundarias deberán agruparse preferentemente mediante `⋯` u otro patrón equivalente.

---

# 19 — Menú contextual

El menú `⋯` deberá utilizarse para acciones secundarias o contextuales.

No utilizarlo como escondite indiscriminado de toda funcionalidad.

Los textos de las acciones deberán ser directos.

Las operaciones destructivas deberán estar visualmente diferenciadas de las acciones normales.

---

# 20 — Popovers, diálogos, drawers y bottom sheets

Utilizar cada patrón según la complejidad y dispositivo.

## Popover

Preferir para:

* pocas opciones;
* acciones contextuales;
* controles próximos al elemento que los invoca.

## Diálogo

Preferir cuando:

* el usuario deba concentrarse en una decisión;
* exista una operación que requiera confirmación;
* exista un flujo breve que no convenga realizar sobre la pantalla principal.

## Drawer

Preferir para:

* conjuntos de opciones más amplios;
* filtros complejos;
* información contextual que deba convivir con la pantalla principal.

## Bottom sheet

Preferir en mobile cuando:

* las opciones deban aparecer desde un control de la pantalla;
* sea más cómodo operar desde la parte inferior;
* el contenido pueda presentarse claramente en ese espacio.

No utilizar modal o diálogo para cualquier operación por defecto.

---

# 21 — Indicadores visuales

Cuando una función posea estado, el control deberá comunicarlo.

Ejemplos:

* filtros activos;
* criterio de orden;
* sincronización pendiente;
* notificaciones;
* estado de OT;
* prioridad.

No depender exclusivamente del color.

Utilizar combinación apropiada de:

* texto;
* icono;
* badge;
* forma;
* posición;
* color.

---

# 22 — Estados y prioridades parametrizadas

Los estados y prioridades configurables por tenant deberán representarse de manera consistente.

La UI no deberá asumir:

* nombres fijos;
* cantidades fijas;
* colores fijos;
* secuencias rígidas no definidas por configuración.

Los componentes deberán trabajar con la semántica estable y representar la configuración correspondiente.

---

# 23 — Iconografía

Utilizar una familia coherente de iconos.

Una misma función debe utilizar el mismo concepto visual en toda la aplicación.

Los iconos no deben sustituir texto cuando su significado pueda resultar ambiguo.

Cuando corresponda utilizar:

* texto;
* tooltip;
* etiqueta accesible.

---

# 24 — Área táctil

Los controles deben ser cómodos de utilizar en dispositivos táctiles.

Como mínimo deberán respetarse los requisitos de accesibilidad aplicables a tamaño y separación de objetivos interactivos.

Cuando sea viable en controles táctiles principales, utilizar áreas de interacción más generosas que el mínimo técnico.

No reducir botones a áreas difíciles de pulsar únicamente para conseguir una interfaz más compacta.

---

# 25 — Accesibilidad

Objetivo mínimo:

**WCAG 2.2 nivel AA en los flujos de aplicación relevantes.**

Considerar desde el diseño:

* navegación mediante teclado;
* foco visible;
* orden lógico de foco;
* contraste;
* labels;
* nombres accesibles;
* semántica;
* tamaño de controles;
* mensajes de error;
* no depender únicamente del color;
* funcionamiento con zoom y diferentes tamaños de viewport.

Los popovers, menús y diálogos deberán gestionar correctamente el foco.

---

# 26 — Estados de interfaz

Toda vista que dependa de datos deberá considerar explícitamente:

* carga;
* contenido disponible;
* sin resultados;
* ausencia inicial de datos;
* error;
* reintento;
* operación exitosa;
* permisos insuficientes cuando corresponda.

Evitar pantallas vacías sin explicación.

---

# 27 — Feedback de operaciones

Cuando el usuario ejecute una acción debe comprender qué ocurrió.

Diferenciar:

* operación iniciada;
* operación en proceso;
* operación completada;
* operación fallida;
* operación pendiente de sincronización.

Nunca presentar como sincronizado aquello que solamente se encuentre almacenado localmente.

---

# 28 — Validaciones

Las validaciones deberán aparecer próximas al dato que debe corregirse.

El mensaje debe explicar qué necesita hacer el usuario.

Evitar mensajes técnicos.

Ejemplo incorrecto:

`Validation error`

Ejemplo preferido:

`Ingresá el CUIT sin caracteres inválidos.`

Las validaciones de frontend no sustituyen las validaciones de API.

---

# 29 — Tema claro y oscuro

La aplicación deberá utilizar design tokens centralizados.

Como mínimo para:

* fondo;
* superficies;
* texto principal;
* texto secundario;
* bordes;
* acciones;
* foco;
* error;
* advertencia;
* éxito;
* estados;
* prioridades.

Evitar colores hardcodeados individualmente por pantalla.

Los componentes deberán funcionar correctamente en tema claro y oscuro.

---

# 30 — Consistencia transversal

Personas, Clientes, Técnicos, Activos, Ubicaciones, OT y futuros módulos deberán utilizar los mismos patrones para funciones equivalentes.

Ejemplos:

* buscar siempre debe sentirse como buscar;
* filtrar siempre debe sentirse como filtrar;
* guardar debe mantener una jerarquía consistente;
* `⋯` debe representar acciones secundarias;
* errores deben comportarse de forma similar;
* estados y prioridades deben mantener el mismo lenguaje visual.

No crear una UX diferente por módulo sin una razón funcional.

---

# 31 — Parametrización y UI

La interfaz debe aceptar configuraciones variables sin romperse.

Considerar:

* textos más largos;
* diferentes nombres de estados;
* diferentes cantidades de estados;
* prioridades personalizadas;
* nombres visibles del tenant;
* branding futuro.

No diseñar componentes basándose únicamente en los valores de la plantilla `DEFAULT`.

---

# 32 — Navegación

La navegación debe adaptarse al dispositivo.

No conservar una navegación desktop que desborde o resulte incómoda en mobile.

La ubicación actual del usuario debe ser comprensible.

Las funciones principales deben permanecer accesibles sin exigir navegación innecesaria.

---

# 33 — Densidad de información

La limpieza visual no implica eliminar información útil.

Priorizar:

1. lo necesario para reconocer;
2. lo necesario para decidir;
3. lo necesario para actuar.

El detalle adicional puede revelarse cuando el usuario lo solicite.

---

# 34 — SDD

Cuando AI-NATIVE / SDD esté activo, toda SPEC que modifique frontend deberá declarar que ha considerado este estándar.

La SPEC deberá definir solamente aquello específico de la feature, como:

* flujo;
* actores;
* información requerida;
* estados particulares;
* permisos;
* comportamiento responsive particular;
* criterios de aceptación;
* excepciones justificadas.

No copiar este documento completo dentro de cada SPEC.

---

# 35 — Evaluación de cada interfaz

Antes de considerar terminada una pantalla relevante, verificar:

* ¿la acción primaria se identifica inmediatamente?;
* ¿hay botones innecesarios permanentemente visibles?;
* ¿las acciones secundarias están agrupadas?;
* ¿buscar es rápido cuando corresponde?;
* ¿los filtros activos son reconocibles?;
* ¿pueden eliminarse fácilmente?;
* ¿funciona correctamente en mobile?;
* ¿funciona correctamente en desktop?;
* ¿existe scroll horizontal innecesario?;
* ¿los controles táctiles son cómodos?;
* ¿el foco es visible?;
* ¿la pantalla funciona en claro y oscuro?;
* ¿se contemplan carga, vacío y error?;
* ¿los textos y valores parametrizados pueden variar?;
* ¿la interfaz mantiene los patrones del resto de GI-OT?

---

# 36 — Skills y herramientas de diseño

Una Skill de diseño/frontend puede ayudar a:

* analizar composición;
* implementar componentes;
* mejorar responsive;
* revisar jerarquía visual;
* detectar inconsistencias;
* proponer una implementación más cuidada.

La Skill es una herramienta de ejecución.

Este documento continúa siendo la fuente de verdad de UI/UX del producto.

Una Skill no debe:

* redefinir el producto;
* cambiar reglas funcionales;
* incorporar una dependencia sin autorización;
* reemplazar el design system existente;
* cambiar el stack;
* ignorar parametrización;
* sacrificar accesibilidad por estética.

---

# Criterio final

La interfaz de `gi-ot` debe sentirse simple aunque el dominio sea complejo.

La complejidad funcional deberá organizarse mediante:

**jerarquía + contexto + revelado progresivo + patrones consistentes**

y no mediante acumulación permanente de botones, campos y opciones.
