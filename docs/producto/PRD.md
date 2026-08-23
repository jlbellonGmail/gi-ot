# PRD v0.1 — gi-ot

## Plataforma SaaS Multirrubro de Gestión de Órdenes de Trabajo

**Proyecto:** gi-ot
**Tipo de producto:** SaaS B2B multitenant
**Mercado inicial:** Argentina
**Estado:** Base funcional para inicio de proyecto
**Versión:** 0.1
**Documento:** `docs/producto/PRD.md`

---

# 1. Propósito del documento

Este documento define el alcance inicial, principios de producto y requerimientos funcionales de **gi-ot**.

Su objetivo es proporcionar una fuente de verdad única para:

* producto;
* diseño;
* arquitectura;
* desarrollo;
* pruebas;
* documentación futura.

El PRD establece **qué debe resolver el producto y qué límites debe respetar**.

Los detalles técnicos de implementación se definirán posteriormente en la arquitectura y, cuando el proyecto ingrese al circuito AI-NATIVE, mediante especificaciones SDD.

---

# 2. Visión del producto

**gi-ot** es una plataforma SaaS multirrubro para gestionar Órdenes de Trabajo.

Su objetivo principal es digitalizar el circuito entre:

**empresa → oficina → técnico → cliente**

permitiendo sustituir progresivamente:

* órdenes en papel;
* anotaciones manuales;
* planillas;
* llamadas;
* mensajes dispersos;
* fotografías sin contexto;
* información almacenada informalmente.

El sistema debe permitir conocer con claridad:

* qué trabajo debe realizarse;
* para quién;
* dónde;
* sobre qué activo;
* quién debe realizarlo;
* cuándo;
* qué se realizó;
* qué evidencias existen;
* en qué estado quedó;
* qué trabajos anteriores recibió ese activo.

---

# 3. Principio rector

gi-ot debe seguir permanentemente este principio:

> **Simple para operar, potente para administrar y flexible para adaptarse a distintos rubros.**

El sistema no debe trasladar complejidad administrativa innecesaria al técnico.

La aplicación utilizada en campo debe permitir completar las operaciones habituales con la menor cantidad posible de pasos.

---

# 4. Modelo de producto

gi-ot será comercializado como:

**Software as a Service — SaaS**

Las empresas contratarán el servicio y utilizarán una plataforma común.

No se construirá un sistema independiente por cliente.

Existirá:

```text
PLATAFORMA gi-ot
        │
        ├── Empresa A
        ├── Empresa B
        ├── Empresa C
        └── Empresa N
```

Cada empresa constituye un:

**Tenant**

---

# 5. Multitenancy

gi-ot debe ser **multitenant desde su primera versión funcional**.

Todas las entidades de negocio deben diseñarse considerando explícitamente su pertenencia a un tenant.

Ejemplo conceptual:

```text
Tenant
 │
 ├── Usuarios
 ├── Configuración
 ├── Clientes
 ├── Ubicaciones
 ├── Activos
 ├── Técnicos
 ├── Órdenes de Trabajo
 └── Historial
```

La información perteneciente a un tenant nunca debe quedar accesible para otro tenant.

La primera implementación comercial puede utilizar inicialmente pocos clientes reales, pero la arquitectura nunca deberá asumir que existe una única empresa.

---

# 6. Aislamiento entre tenants

El aislamiento de información es una regla estructural del producto.

Cada entidad funcional deberá estar relacionada directa o indirectamente con su tenant.

El sistema debe impedir:

* acceso cruzado entre empresas;
* consultas de información perteneciente a otro tenant;
* modificación de información ajena;
* referencias entre entidades de diferentes tenants;
* exposición accidental de archivos o fotografías de otra empresa.

Este principio deberá verificarse posteriormente mediante pruebas específicas.

---

# 7. Modelo comercial inicial

El producto contempla tres fuentes potenciales de ingresos:

```text
gi-ot
 │
 ├── Suscripción SaaS
 │
 ├── Planes / funcionalidades
 │
 └── Servicios de personalización
```

El núcleo del producto será común para todos los clientes.

Las diferencias entre empresas deben resolverse prioritariamente mediante:

**configuración y parametrización.**

Las personalizaciones mediante desarrollo específico deberán ser excepcionales y comercializadas separadamente cuando corresponda.

---

# 8. Filosofía de parametrización

gi-ot debe evitar conceptos rígidos asociados a un rubro particular.

Debe existir:

```text
NÚCLEO FUNCIONAL ESTABLE
          +
PARAMETRIZACIÓN POR TENANT
```

La parametrización permitirá adaptar el producto sin generar una versión diferente del software para cada cliente.

---

# 9. Qué debe ser parametrizable

El sistema debe prepararse para permitir parametrización por tenant de conceptos como:

* denominaciones visibles;
* tipos de activo;
* estados de OT;
* prioridades;
* tipos de trabajo;
* motivos de no resolución;
* categorías;
* datos de empresa;
* textos;
* comprobantes;
* preferencias operativas;
* configuración de notificaciones;
* branding básico;
* campos opcionales.

No significa que todos estos parámetros deban implementarse durante la primera iteración.

La arquitectura debe permitir incorporarlos progresivamente.

---

# 10. Identificadores internos y etiquetas visibles

Los conceptos centrales deberán tener identificadores internos estables.

Ejemplo:

```text
PENDING
IN_PROGRESS
COMPLETED
UNRESOLVED
```

Una empresa podría visualizarlos como:

```text
Pendiente
En trabajo
Finalizada
Requiere nueva visita
```

Mientras otra empresa podría configurarlos como:

```text
Asignada
En atención
Servicio realizado
Pendiente de repuesto
```

El comportamiento interno del sistema no debe depender exclusivamente del texto visible.

---

# 11. Arquitectura multirrubro

El sistema deberá poder utilizarse en actividades como:

* climatización;
* refrigeración;
* electricidad;
* plomería;
* alarmas;
* seguridad;
* ascensores;
* mantenimiento edilicio;
* mantenimiento industrial;
* control de plagas;
* servicios técnicos;
* reparación de equipos;
* instalaciones;
* otros servicios de campo.

El producto no debe incluir terminología obligatoria de un rubro particular.

---

# 12. Concepto de Activo

El elemento sobre el cual se ejecuta un trabajo se denominará internamente:

**Activo**

Un activo puede representar:

* equipo;
* máquina;
* instalación;
* dispositivo;
* vehículo;
* infraestructura;
* habitación;
* sector;
* elemento técnico;
* cualquier objeto mantenible.

La etiqueta **Activo** podrá mostrarse de otra forma para cada tenant.

Ejemplo:

```text
Activo
→ Equipo

Activo
→ Instalación

Activo
→ Máquina
```

---

# 13. Modelo jerárquico básico

La estructura principal será:

```text
Empresa / Tenant
       │
       └── Cliente
             │
             └── Ubicación
                    │
                    └── Activo
```

Ejemplo:

```text
Tenant:
Servicio Técnico Córdoba

Cliente:
Supermercados Norte

Ubicación:
Sucursal Centro

Activos:
- Cámara frigorífica 01
- Cámara frigorífica 02
- Aire acondicionado salón
```

---

# 14. Problema que resuelve

Las empresas objetivo suelen gestionar actualmente sus servicios mediante una combinación de:

* papel;
* WhatsApp;
* llamadas;
* fotografías;
* Excel;
* correo electrónico;
* sistemas aislados.

Esto genera:

* pérdida de información;
* órdenes ilegibles;
* demora administrativa;
* falta de trazabilidad;
* trabajos sin documentar;
* dificultad para facturar;
* información técnica dispersa;
* desconocimiento del historial de los equipos;
* imposibilidad de conocer rápidamente el estado de los trabajos.

gi-ot centralizará ese circuito.

---

# 15. Objetivo principal del MVP

El MVP debe permitir que una empresa pueda administrar digitalmente el circuito completo:

```text
CREAR
  ↓
ASIGNAR
  ↓
EJECUTAR
  ↓
DOCUMENTAR
  ↓
CERRAR
  ↓
CONSULTAR
```

una Orden de Trabajo.

---

# 16. Actores del sistema

El sistema contempla inicialmente cuatro perfiles principales.

```text
PLATAFORMA gi-ot
│
├── PROPIETARIO / SUPERADMINISTRADOR
│
└── TENANT
    │
    ├── ADMINISTRADOR EMPRESA
    │
    ├── ADMINISTRATIVO
    │
    └── TÉCNICO
```

---

# 17. Propietario / Superadministrador SaaS

Es el rol reservado a los propietarios u operadores de gi-ot.

No pertenece funcionalmente a una empresa cliente.

Podrá administrar la plataforma.

Funciones futuras previstas:

* crear tenants;
* consultar tenants;
* habilitar empresas;
* suspender empresas;
* gestionar planes;
* gestionar suscripciones;
* consultar utilización;
* proporcionar soporte;
* administrar configuración global;
* consultar estado general de la plataforma.

Las funciones comerciales avanzadas no son necesarias para la primera iteración, pero el rol debe existir desde el diseño inicial.

---

# 18. Administrador de empresa

Es el máximo nivel dentro de cada tenant.

Puede administrar:

* datos de su empresa;
* usuarios;
* técnicos;
* roles;
* parámetros;
* clientes;
* ubicaciones;
* activos;
* órdenes;
* configuraciones.

Nunca podrá administrar otra empresa.

---

# 19. Usuario administrativo

Representa al personal de oficina.

Podrá realizar tareas como:

* consultar clientes;
* crear clientes;
* consultar ubicaciones;
* administrar activos;
* crear OT;
* asignar OT;
* consultar técnicos;
* modificar información administrativa;
* visualizar estados;
* consultar órdenes terminadas;
* buscar historial;
* generar comprobantes.

Sus permisos específicos podrán evolucionar.

---

# 20. Técnico

Representa al usuario que ejecuta trabajos en campo.

Por defecto podrá:

* consultar sus órdenes;
* abrir una OT;
* iniciar trabajo;
* registrar trabajo realizado;
* utilizar dictado por voz;
* tomar fotografías;
* identificar activos mediante QR;
* cambiar estado;
* finalizar una orden;
* crear una OT urgente;
* consultar información necesaria del activo;
* operar sin conexión.

Por defecto no tendrá acceso administrativo completo.

El rol operativo de Técnico es independiente de disponer o no de acceso al sistema (usuario con rol `TENANT_TECHNICIAN`): son dos conceptos distintos. Internamente, "Técnico" es una especialización de una entidad de persona compartida con "Cliente", para no duplicar los datos de una misma persona que cumple ambas funciones (detalle en `docs/tecnica/modelo-datos.md` §10; esto es transparente para quien usa el sistema).

---

# 21. Roles y permisos

La arquitectura deberá contemplar:

**RBAC — Role Based Access Control.**

Los cuatro roles iniciales constituyen perfiles predeterminados.

En una evolución posterior podrán existir:

* roles personalizados;
* permisos individuales;
* combinaciones de permisos.

El MVP no deberá implementar un sistema excesivamente complejo de permisos.

---

# 22. Cliente

Un cliente representa la persona u organización que recibe el servicio.

Datos mínimos previstos:

* nombre o razón social;
* identificación;
* teléfono;
* email;
* observaciones;
* estado activo/inactivo.

Los datos fiscales avanzados quedan fuera del MVP.

Internamente, un Cliente es una especialización de una entidad de persona compartida con "Técnico": una misma persona puede ser Cliente y Técnico a la vez sin que sus datos generales queden duplicados. El alta se hace siempre desde el concepto "Cliente"; el usuario nunca necesita conocer ni operar esa entidad interna (detalle en `docs/tecnica/modelo-datos.md` §10).

---

# 23. Ubicaciones

Un cliente puede disponer de una o múltiples ubicaciones.

Ejemplos:

* casa;
* sucursal;
* planta;
* depósito;
* edificio;
* oficina;
* local.

Datos mínimos:

* nombre;
* dirección;
* localidad;
* provincia;
* observaciones.

---

# 24. Activos

Un activo pertenece normalmente a una ubicación.

Datos previstos:

* identificador;
* nombre;
* tipo;
* descripción;
* marca;
* modelo;
* número de serie;
* código interno;
* observaciones;
* estado;
* QR.

No todos serán obligatorios.

Debe ser posible crear un activo únicamente con información mínima.

Ejemplo:

```text
Aire acondicionado oficina gerente
```

---

# 25. Tipos de activo

Los tipos de activo deben ser parametrizables por tenant.

Ejemplo para climatización:

```text
Split
Rooftop
Cámara frigorífica
Chiller
```

Ejemplo para ascensores:

```text
Ascensor
Montacargas
Plataforma
```

El sistema no deberá contener una lista rígida universal.

---

# 26. Código QR

Cada activo podrá disponer de un código QR.

Flujo esperado:

```text
Abrir cámara
     ↓
Escanear QR
     ↓
Identificar activo
     ↓
Ver información
     ↓
Consultar historial / ejecutar OT
```

El QR deberá contener únicamente un identificador seguro.

No debe almacenar información confidencial directamente.

---

# 27. Orden de Trabajo

La Orden de Trabajo constituye la entidad funcional central de gi-ot.

Debe permitir responder:

* quién solicitó el trabajo;
* dónde debe realizarse;
* sobre qué activo;
* quién es responsable;
* qué debe hacerse;
* qué se realizó;
* cuándo;
* cuál fue el resultado;
* qué evidencias existen.

---

# 28. Datos principales de una OT

Una OT podrá incluir:

* número;
* tenant;
* cliente;
* ubicación;
* activo;
* técnico responsable;
* fecha programada;
* prioridad;
* tipo de trabajo;
* descripción solicitada;
* fecha/hora de inicio;
* trabajo realizado;
* observaciones;
* estado;
* fecha/hora de finalización;
* fotografías;
* usuario creador;
* fecha de creación;
* última modificación.

No todos los datos serán obligatorios.

---

# 29. Estados de OT

Los estados deben ser configurables.

El sistema podrá proporcionar inicialmente un conjunto estándar:

```text
Pendiente
En proceso
Terminada
No resuelta
```

pero cada tenant podrá adaptar posteriormente sus denominaciones y determinadas configuraciones.

El núcleo debe conservar suficiente semántica interna para mantener consistente el funcionamiento del producto.

---

# 30. Prioridades

Las prioridades también deberán poder parametrizarse.

Configuración inicial sugerida:

```text
Baja
Normal
Alta
Urgente
```

No deberán codificarse como textos rígidos dentro de la aplicación.

---

# 31. Tipos de trabajo

Cada tenant podrá definir sus propios tipos.

Ejemplo:

```text
Correctivo
Preventivo
Instalación
Revisión
Inspección
Garantía
```

Estos conceptos pueden variar significativamente según el rubro.

---

# 32. Flujo planificado

La oficina:

```text
Selecciona cliente
       ↓
Selecciona ubicación
       ↓
Selecciona activo
       ↓
Describe trabajo
       ↓
Asigna técnico
       ↓
Programa
```

El técnico recibe la OT.

Posteriormente:

```text
Abre OT
   ↓
Inicia
   ↓
Realiza trabajo
   ↓
Registra resultado
   ↓
Adjunta evidencias
   ↓
Finaliza
```

---

# 33. Flujo de urgencia

Debe existir un circuito no planificado.

Ejemplo:

Durante una visita aparece otro problema que necesita atención.

El técnico puede:

```text
Crear nueva OT
     ↓
Seleccionar cliente
     ↓
Seleccionar ubicación
     ↓
Seleccionar activo
     ↓
Registrar problema
     ↓
Ejecutar
     ↓
Finalizar
```

No deberá depender obligatoriamente de que la oficina cree previamente la orden.

---

# 34. Experiencia mobile-first

El flujo técnico debe diseñarse prioritariamente para teléfonos.

Principios:

* botones grandes;
* pocos campos;
* mínimo desplazamiento;
* acciones evidentes;
* carga rápida;
* utilización con una mano cuando sea posible;
* compatibilidad con cámara;
* dictado por voz;
* tolerancia a mala conectividad.

El flujo ideal será:

```text
ABRIR
 ↓
HACER
 ↓
REGISTRAR
 ↓
TERMINAR
```

---

# 35. Dictado por voz

Los campos descriptivos deberán poder aprovechar el dictado por voz proporcionado por el dispositivo cuando esté disponible.

No será necesario desarrollar inicialmente un motor propio de reconocimiento de voz.

---

# 36. Fotografías

Una OT podrá contener múltiples fotografías.

Ejemplos:

* estado inicial;
* equipo;
* daño;
* reparación;
* pieza reemplazada;
* trabajo finalizado;
* documentación.

Las fotografías no serán obligatorias por defecto.

Más adelante podrán configurarse reglas específicas según tenant o tipo de trabajo.

---

# 37. Firma del cliente

La firma del cliente queda fuera del núcleo obligatorio del MVP inicial.

La arquitectura debe permitir incorporarla posteriormente.

---

# 38. Geolocalización

La optimización de rutas queda fuera del MVP.

Sin embargo podrá almacenarse opcionalmente una posición aproximada asociada a determinados eventos, por ejemplo:

* inicio;
* finalización.

Su utilización deberá respetar permisos del dispositivo y políticas aplicables.

No deberá bloquear el trabajo cuando la geolocalización no esté disponible.

---

# 39. Funcionamiento offline

El funcionamiento sin conexión constituye un requerimiento central.

El técnico debe poder continuar trabajando cuando no tenga:

* Wi-Fi;
* 4G;
* 5G.

Debe ser posible:

* consultar información necesaria previamente sincronizada;
* abrir OT;
* modificar OT;
* escribir observaciones;
* tomar fotografías;
* registrar trabajo;
* finalizar trabajo.

---

# 40. Sincronización

Cuando vuelva la conectividad:

```text
Dispositivo
    ↓
Detecta conexión
    ↓
Procesa cambios pendientes
    ↓
Sincroniza
    ↓
Servidor
```

La sincronización deberá ocurrir preferentemente en segundo plano.

El técnico no debería necesitar comprender internamente el mecanismo de sincronización.

---

# 41. Estado de sincronización

La interfaz deberá comunicar claramente estados como:

```text
Sincronizado
Pendiente de sincronización
Sincronizando
Error de sincronización
```

Nunca deberá aparentar que información no enviada ya se encuentra confirmada en el servidor.

---

# 42. Conflictos

Para reducir complejidad, cada OT tendrá inicialmente un técnico responsable principal.

La ejecución de campo será modificada principalmente por ese técnico.

Esto reduce los conflictos de edición concurrente.

Los conflictos excepcionales deberán poder detectarse y registrarse.

No se construirá inicialmente un motor complejo de edición colaborativa.

---

# 43. Panel de oficina

El panel web deberá permitir conocer rápidamente:

* OT pendientes;
* OT en proceso;
* OT terminadas;
* OT no resueltas;
* técnicos;
* clientes;
* actividad reciente.

La prioridad será funcionalidad y claridad.

No se requiere inicialmente BI avanzado.

---

# 44. Consulta de órdenes

Las OT deberán poder filtrarse por criterios como:

* fechas;
* técnico;
* cliente;
* ubicación;
* activo;
* estado;
* prioridad;
* tipo.

También deberá existir búsqueda textual.

---

# 45. Historial del activo

Cada activo deberá conservar su historial de intervenciones.

Ejemplo:

```text
Cámara frigorífica 01

12/03/2026
Cambio de termostato

21/05/2026
Mantenimiento preventivo

14/08/2026
Cambio de ventilador
```

Este historial constituye uno de los valores centrales del producto.

---

# 46. Historial del cliente

También podrá consultarse:

```text
Cliente
   ↓
Ubicaciones
   ↓
Activos
   ↓
Órdenes
```

Esto permitirá obtener rápidamente el historial completo de servicio.

---

# 47. Comprobante de trabajo

Al terminar una OT podrá generarse un comprobante digital.

Podrá incluir:

* identidad de empresa;
* número de OT;
* cliente;
* ubicación;
* activo;
* fecha;
* técnico;
* trabajo solicitado;
* trabajo realizado;
* resultado.

El formato deberá permitir personalización progresiva.

---

# 48. Notificaciones

El cierre de una OT podrá disparar una notificación al cliente.

Canales previstos:

* email;
* WhatsApp.

La implementación inicial utilizará el mecanismo que resulte más simple y fiable.

Los demás canales podrán incorporarse posteriormente.

---

# 49. Reapertura de OT

Una OT cerrada no deberá modificarse libremente.

Podrá existir una reapertura controlada por un usuario autorizado.

La reapertura deberá preservar trazabilidad.

Un técnico común no podrá modificar arbitrariamente una OT terminada.

---

# 50. Técnicos por OT

Para mantener simple el MVP:

**una OT tendrá un técnico responsable principal.**

En evoluciones posteriores se podrá contemplar:

* colaboradores;
* cuadrillas;
* múltiples responsables.

---

# 51. Activos por OT

Para mantener un historial simple y preciso:

**una OT estará asociada principalmente a un activo.**

Cuando una visita involucre varios activos podrán generarse diferentes OT relacionadas.

En una evolución futura podrá incorporarse un concepto explícito de visita o agrupador de órdenes.

---

# 52. Materiales

La gestión de inventario y stock queda fuera del MVP.

Podrá incorporarse inicialmente o posteriormente un campo meramente informativo de materiales utilizados.

Este registro no implicará movimientos automáticos de inventario.

---

# 53. Administración de parámetros

El administrador del tenant deberá disponer progresivamente de herramientas para administrar sus parámetros sin solicitar modificaciones de software.

Ejemplos:

```text
Configuración
│
├── Estados
├── Prioridades
├── Tipos de activo
├── Tipos de trabajo
├── Motivos
└── Preferencias
```

La interfaz exacta se definirá durante el diseño funcional.

---

# 54. Branding por tenant

Cada empresa podrá disponer progresivamente de su identidad visual.

Ejemplos:

* nombre comercial;
* logo;
* datos de contacto;
* información del comprobante;
* determinados colores.

La personalización no deberá comprometer la coherencia general del producto.

---

# 55. Seguridad

Desde la primera versión deberán contemplarse:

* autenticación;
* autorización;
* multitenancy;
* aislamiento de datos;
* HTTPS;
* almacenamiento seguro de credenciales;
* trazabilidad;
* gestión de sesiones;
* respaldo.

Nunca se almacenarán contraseñas en texto plano.

---

# 56. Auditoría básica

Se deberá registrar como mínimo cuando corresponda:

* fecha de creación;
* usuario creador;
* fecha de modificación;
* usuario modificador;
* técnico responsable;
* inicio;
* finalización;
* cambios relevantes de estado.

Una auditoría exhaustiva campo por campo puede implementarse posteriormente.

---

# 57. Alcance funcional del MVP

El MVP debe cubrir:

```text
SaaS multitenant
      +
Autenticación
      +
Roles
      +
Parametrización básica
      +
Clientes
      +
Ubicaciones
      +
Activos
      +
Técnicos
      +
Órdenes
      +
Experiencia móvil
      +
QR
      +
Fotografías
      +
Offline
      +
Sincronización
      +
Historial
      +
Panel oficina
      +
Comprobante
```

---

# 58. Fuera del MVP

Quedan inicialmente fuera:

* facturación electrónica;
* ARCA;
* contabilidad;
* cobranzas;
* pagos;
* sueldos;
* liquidación de personal;
* inventario completo;
* compras;
* proveedores;
* optimización de rutas;
* GPS permanente;
* CRM completo;
* presupuestos;
* contratos;
* portal de clientes;
* mantenimiento predictivo;
* inteligencia artificial avanzada;
* Business Intelligence avanzado;
* ERP;
* integraciones empresariales complejas.

Estas funcionalidades podrán evolucionar como módulos.

---

# 59. Arquitectura modular futura

gi-ot debe funcionar como núcleo de un ecosistema.

```text
                 FACTURACIÓN
                      │
                      │
 STOCK ──────────── gi-ot ─────────── CRM
                      │
                      │
               PLANIFICACIÓN
```

Los módulos futuros no deben contaminar la simplicidad del núcleo actual.

---

# 60. Dispositivos

El producto deberá funcionar adecuadamente en:

* teléfonos Android;
* iPhone;
* tablets;
* notebooks;
* computadoras de escritorio.

---

# 61. Estrategia de aplicación móvil

Se priorizará inicialmente una arquitectura web responsive / PWA cuando permita satisfacer:

* funcionamiento offline;
* cámara;
* fotografías;
* QR;
* almacenamiento local;
* sincronización;
* experiencia de instalación adecuada.

Solo se elegirá desarrollo móvil nativo si existe una razón técnica o comercial demostrable.

---

# 62. Entidades conceptuales iniciales

El diseño conceptual debe contemplar al menos:

```text
Tenant
TenantConfig

User
Role
Permission

Person
PersonIdentification
Customer        (especialización de Person)
Technician       (especialización de Person)

Location
Asset
AssetType

WorkOrder
WorkOrderStatus
WorkOrderType
Priority

WorkOrderPhoto
WorkOrderHistory

Notification

SyncOperation
```

`Customer` y `Technician` comparten una única base de datos de persona (`Person`) para que una misma persona real con más de una función dentro del tenant nunca quede duplicada; ver `docs/tecnica/modelo-datos.md` §10.

El diseño físico definitivo se determinará durante la etapa de arquitectura.

---

# 63. Relaciones principales

```text
Tenant
 │
 ├── Users
 ├── Configuration
 ├── Technicians
 │
 ├── Clients
 │     │
 │     └── Locations
 │            │
 │            └── Assets
 │
 └── Work Orders
```

Y:

```text
Work Order
 │
 ├── Tenant
 ├── Client
 ├── Location
 ├── Asset
 ├── Technician
 ├── Status
 ├── Priority
 ├── Type
 ├── Photos
 └── History
```

---

# 64. Requisitos no funcionales

## Simplicidad

Las operaciones habituales deben requerir pocos pasos.

## Mobile First

El técnico es un usuario principal del sistema.

## Rendimiento

Las acciones frecuentes deben responder rápidamente.

## Offline First para campo

La pérdida de conectividad no debe provocar pérdida de información.

## Seguridad

El tenant constituye una frontera obligatoria de seguridad.

## Parametrización

Las diferencias razonables entre rubros deben resolverse mediante configuración.

## Extensibilidad

El producto debe permitir crecer modularmente.

## Trazabilidad

Debe poder determinarse quién realizó una operación relevante y cuándo.

## Mantenibilidad

Debe existir un único producto base, evitando forks por cliente.

---

# 65. Criterio de éxito del MVP

El MVP será considerado operativo cuando pueda completarse correctamente este escenario:

```text
1. Crear un tenant.

2. Crear administrador de empresa.

3. Crear usuario administrativo.

4. Crear técnico.

5. Configurar parámetros básicos.

6. Crear cliente.

7. Crear ubicación.

8. Crear activo.

9. Crear una OT.

10. Asignarla.

11. Técnico recibe OT.

12. Técnico puede trabajar sin conexión.

13. Técnico registra trabajo.

14. Adjunta fotografía.

15. Finaliza OT.

16. Recupera conexión.

17. La información se sincroniza.

18. Oficina visualiza el resultado.

19. El activo conserva historial.

20. Se genera comprobante.

21. El cliente puede recibir la notificación.

22. Otro tenant no puede acceder a ninguna de estas entidades.
```

---

# 66. Métrica principal del producto

La métrica inicial no será cantidad de funciones.

La pregunta será:

> **¿Puede una empresa abandonar el papel y gestionar de punta a punta sus Órdenes de Trabajo utilizando gi-ot?**

Si la respuesta es afirmativa, el núcleo del MVP habrá cumplido su objetivo.

---

# 67. Regla de simplicidad

Toda nueva funcionalidad deberá responder:

1. ¿Es necesaria para ejecutar una OT?
2. ¿Es necesaria para administrar una OT?
3. ¿Impide operar a un cliente real si no existe?
4. ¿Debe realmente implementarse ahora?

Si no cumple estos criterios:

**se incorpora al backlog futuro.**

---

# 68. Regla de personalización

Antes de desarrollar una funcionalidad específica para un cliente deberá evaluarse:

```text
¿Puede resolverse mediante parámetro?
             │
        SÍ ──┴── NO
        │         │
CONFIGURAR     evaluar
              desarrollo
              adicional
```

La personalización mediante código será la excepción y no la regla.

---

# 69. Estrategia inicial de construcción

El proyecto comenzará en modo:

**BOOTSTRAP**

Esto significa avanzar rápidamente sobre el producto sin ejecutar todavía todo el circuito formal AI-NATIVE.

Secuencia inicial:

```text
PRD
 ↓
Modelo funcional
 ↓
Flujos
 ↓
Modelo de datos
 ↓
Arquitectura
 ↓
Wireframes
 ↓
Construcción
 ↓
MVP inicial
```

---

# 70. Compatibilidad AI-NATIVE

Aunque el circuito formal no se utilice inicialmente, el proyecto nacerá dentro de una estructura compatible con el template AI-NATIVE.

No se construirá una aplicación temporal para migrarla posteriormente.

Se construirá desde el comienzo dentro de su estructura definitiva.

---

# 71. Activación futura de SDD

Cuando la base funcional sea suficientemente estable:

```text
BOOTSTRAP
    ↓
Revisión de arquitectura
    ↓
Normalización del ROADMAP
    ↓
Especificaciones SDD
    ↓
Features
    ↓
Circuito AI-NATIVE
```

Desde ese momento se utilizarán las reglas formales de:

* planificación;
* construcción;
* auditoría;
* evidencia;
* HITL;
* Git;
* CI/CD.

---

# 72. Roadmap macro

## Etapa 00 — Definición

* PRD;
* modelo funcional;
* flujos;
* modelo conceptual;
* arquitectura;
* wireframes.

## Etapa 01 — Fundación SaaS

* aplicación base;
* multitenancy;
* autenticación;
* autorización;
* roles;
* configuración por tenant.

## Etapa 02 — Maestros

* clientes;
* ubicaciones;
* activos;
* tipos;
* técnicos.

## Etapa 03 — Núcleo OT

* creación;
* asignación;
* consulta;
* ejecución;
* cierre;
* historial.

## Etapa 04 — Experiencia móvil

* mobile first;
* QR;
* cámara;
* fotografías;
* urgencias.

## Etapa 05 — Offline

* almacenamiento local;
* operaciones pendientes;
* sincronización;
* recuperación;
* conflictos básicos.

## Etapa 06 — Oficina

* panel;
* búsqueda;
* filtros;
* seguimiento;
* históricos.

## Etapa 07 — Comunicación

* comprobantes;
* email;
* WhatsApp según evolución.

## Etapa 08 — Consolidación

* pruebas;
* seguridad;
* UX;
* datos reales;
* piloto.

## Etapa 09 — Industrialización AI-NATIVE

* Git formal;
* SDD;
* features;
* agentes;
* auditoría;
* HITL;
* CI/CD.

---

# 73. Fuente de verdad

A partir del inicio del proyecto:

**`docs/producto/PRD.md` constituye la fuente de verdad principal respecto del alcance funcional del producto.**

Los documentos posteriores deberán complementar este PRD sin contradecirlo.

Las decisiones técnicas se documentarán separadamente.

Las nuevas ideas deberán evaluarse antes de incorporarse al alcance.

---

# 74. Documentos derivados

A partir de este PRD deberán crearse progresivamente:

```text
docs/producto/
│
├── PRD.md
├── modelo-funcional.md
└── decisiones-producto.md

docs/tecnica/
│
├── arquitectura.md
└── modelo-datos.md
```

El PRD no debe convertirse en documentación técnica detallada.

---

# 75. Próximo hito

El siguiente trabajo del proyecto deberá producir:

**Modelo funcional v0.1**

incluyendo como mínimo:

```text
PLATAFORMA
     ↓
TENANT
     ↓
USUARIOS / ROLES
     ↓
CLIENTES
     ↓
UBICACIONES
     ↓
ACTIVOS
     ↓
ÓRDENES DE TRABAJO
```

y los dos flujos principales:

```text
OFICINA
Crear → Asignar → Seguir → Consultar
```

```text
TÉCNICO
Recibir → Iniciar → Ejecutar → Registrar → Cerrar
```

---

# 76. Decisión de producto consolidada

gi-ot queda definido como:

> **Una plataforma SaaS multitenant, multirrubro, mobile-first y parametrizable para administrar el ciclo completo de Órdenes de Trabajo y conservar el historial operativo de los activos de los clientes.**

El producto deberá permitir comercializar una solución estándar mediante suscripción y ofrecer configuración o personalización adicional cuando exista una necesidad comercial justificada.

La simplicidad operativa deberá preservarse durante toda su evolución.
