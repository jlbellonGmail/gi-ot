# Wireframes principales v0.1 — gi-ot

**Estado:** BOOTSTRAP
**Fuente de verdad:** `docs/producto/PRD.md`, `docs/producto/modelo-funcional.md`
**Documento:** `docs/producto/wireframes.md`

Wireframes textuales de las pantallas mínimas necesarias para iniciar el MVP. No es diseño gráfico definitivo — se resolverá durante la construcción. Cada pantalla indica propósito, información principal, acciones principales y navegación.

---

## 1. Técnico (mobile-first)

Superficie de uso más frecuente del sistema. El objetivo es que las operaciones habituales (recibir, iniciar, registrar, cerrar) requieran el mínimo de pasos posible (PRD §34).

### 1.1 Login

```text
┌─────────────────────────┐
│         gi-ot            │
│                          │
│  [ Email            ]   │
│  [ Contraseña       ]   │
│                          │
│      [ Ingresar ]       │
└─────────────────────────┘
```
- **Propósito:** autenticar al usuario (técnico, oficina o admin — pantalla compartida).
- **Información principal:** campos email/contraseña.
- **Acciones principales:** ingresar.
- **Navegación:** al autenticar, redirige según rol; para `TENANT_TECHNICIAN` → Mis OT.

### 1.2 Mis OT

```text
┌─────────────────────────┐
│ gi-ot        [●Sync]    │
│─────────────────────────│
│ [Todas ▾] [Hoy ▾]       │
│─────────────────────────│
│ ● OT-104  Urgente        │
│   Cámara frigorífica 01  │
│   Sup. Norte - Centro    │
│─────────────────────────│
│ ● OT-101  Normal         │
│   Split oficina gerencia │
│   Pendiente               │
│─────────────────────────│
│         [ + Nueva OT ]  │
└─────────────────────────┘
```
- **Propósito:** que el técnico vea de un vistazo sus OT asignadas.
- **Información principal:** número de OT, prioridad, activo, ubicación, estado; indicador de sincronización siempre visible (arriba).
- **Acciones principales:** abrir una OT (tap en la fila); crear OT urgente (`+ Nueva OT`, flujo de urgencia — modelo-funcional §7/§8).
- **Navegación:** tap en fila → Detalle de OT. `+ Nueva OT` → variante reducida de Detalle de OT en modo creación (mismo formulario mínimo: cliente/ubicación/activo/descripción).

### 1.3 Detalle de OT

```text
┌─────────────────────────┐
│ ← OT-101       [●Sync]  │
│─────────────────────────│
│ Split oficina gerencia   │
│ Sup. Norte - Sucursal    │
│ Centro                   │
│                          │
│ Solicitado:               │
│ "No enfría correctamente"│
│                          │
│ Prioridad: Normal        │
│ Estado: Pendiente         │
│                          │
│    [ Iniciar trabajo ]  │
└─────────────────────────┘
```
- **Propósito:** que el técnico vea todo lo necesario del trabajo antes de empezar.
- **Información principal:** cliente/ubicación/activo, descripción solicitada, prioridad, tipo, estado actual.
- **Acciones principales:** iniciar trabajo (única acción destacada mientras está pendiente).
- **Navegación:** ← vuelve a Mis OT. Al iniciar → Iniciar trabajo (o directamente a Registrar trabajo si "iniciar" es solo un cambio de estado sin pantalla propia).

### 1.4 Iniciar trabajo

```text
┌─────────────────────────┐
│ ← OT-101       [●Sync]  │
│─────────────────────────│
│                          │
│   ¿Iniciar este          │
│   trabajo ahora?         │
│                          │
│   [ Confirmar inicio ]  │
│                          │
└─────────────────────────┘
```
- **Propósito:** confirmar el paso `PENDIENTE → EN PROCESO` (modelo-funcional §9).
- **Información principal:** confirmación simple, sin formulario.
- **Acciones principales:** confirmar inicio.
- **Navegación:** al confirmar → Registrar trabajo realizado (la OT ya queda "en proceso").

### 1.5 Registrar trabajo realizado

```text
┌─────────────────────────┐
│ ← OT-101       [●Sync]  │
│─────────────────────────│
│ Trabajo realizado:        │
│ [ 🎤  Escribir o dictar ] │
│ [                     ]  │
│ [                     ]  │
│                          │
│ [ 📷 Agregar fotos (2) ] │
│                          │
│ Estado: [En proceso ▾]  │
│                          │
│      [ Finalizar OT ]   │
└─────────────────────────┘
```
- **Propósito:** que el técnico documente lo hecho, con el mínimo esfuerzo posible (texto o dictado por voz — PRD §35).
- **Información principal:** descripción del trabajo realizado, contador de fotos adjuntas, estado actual.
- **Acciones principales:** dictar/escribir descripción; agregar fotos; cambiar estado; finalizar OT.
- **Navegación:** botón de fotos → Fotografías (o captura inline sin cambiar de pantalla, a decidir en construcción). Estado → selector inline (ver 1.7). Finalizar → Finalizar OT.

### 1.6 Fotografías

```text
┌─────────────────────────┐
│ ← Fotos OT-101 [●Sync]  │
│─────────────────────────│
│ [img] [img] [img] [ + ] │
│                          │
│  Tap en una foto para    │
│  ver / eliminar          │
└─────────────────────────┘
```
- **Propósito:** adjuntar y revisar evidencia visual del trabajo (WorkOrderPhoto).
- **Información principal:** grilla de fotos ya tomadas/adjuntas.
- **Acciones principales:** tomar foto nueva (`+`, abre cámara del dispositivo), ver/eliminar una foto existente.
- **Navegación:** ← vuelve a Registrar trabajo realizado.

### 1.7 Cambio de estado

```text
┌─────────────────────────┐
│ Cambiar estado           │
│─────────────────────────│
│ ○ En proceso              │
│ ○ Terminada                │
│ ○ No resuelta               │
│                          │
│      [ Confirmar ]      │
└─────────────────────────┘
```
- **Propósito:** cambiar el estado de la OT dentro de las transiciones permitidas (modelo-funcional §9).
- **Información principal:** estados disponibles (catálogo `WorkOrderStatus` parametrizado del tenant).
- **Acciones principales:** seleccionar y confirmar.
- **Navegación:** se abre como selector desde Registrar trabajo realizado; confirmar vuelve a esa misma pantalla con el estado actualizado.

### 1.8 Finalizar OT

```text
┌─────────────────────────┐
│ ← OT-101       [●Sync]  │
│─────────────────────────│
│  Resultado:                │
│  ○ Terminada                │
│  ○ No resuelta               │
│                          │
│  Resumen del trabajo:      │
│  "Cambio de capacitor,    │
│   equipo enfría normal"   │
│  2 fotos adjuntas          │
│                          │
│   [ Confirmar cierre ]  │
└─────────────────────────┘
```
- **Propósito:** cerrar la OT (`EN PROCESO → TERMINADA/NO RESUELTA`), último paso del flujo técnico.
- **Información principal:** resultado final, resumen de lo cargado (descripción, cantidad de fotos) para revisión antes de confirmar.
- **Acciones principales:** elegir resultado, confirmar cierre.
- **Navegación:** al confirmar → vuelve a Mis OT; la OT sale de la lista de pendientes/en proceso.

### 1.9 Indicador de sincronización/offline

No es una pantalla — es un componente persistente visible en el encabezado de toda pantalla técnica (Mis OT, Detalle, Registrar, Fotos, Finalizar), conforme a `arquitectura.md` §8.2 y PRD §41:

```text
[●Sync]   → Sincronizado
[◐Pend]   → Pendiente de sincronización
[↻Sync…]  → Sincronizando
[!Error]  → Error de sincronización
```

Nunca debe mostrarse como "Sincronizado" una operación que solo existe en el dispositivo.

---

## 2. Oficina (web/responsive)

### 2.1 Login

Misma pantalla que 1.1. Al autenticar, un usuario con rol `TENANT_OFFICE` o `TENANT_ADMIN` es redirigido a Inicio.

### 2.2 Inicio

```text
┌───────────────────────────────────────┐
│ gi-ot   Inicio  Clientes  OT   [User▾] │
│─────────────────────────────────────────│
│  Pendientes: 12   En proceso: 5         │
│  Terminadas hoy: 8  No resueltas: 1     │
│─────────────────────────────────────────│
│  Actividad reciente                      │
│  - OT-101 iniciada por Juan Pérez        │
│  - OT-098 finalizada                     │
└───────────────────────────────────────┘
```
- **Propósito:** panorama rápido del estado operativo (PRD §43).
- **Información principal:** conteo de OT por estado, actividad reciente.
- **Acciones principales:** ninguna transaccional; solo navegación.
- **Navegación:** menú superior → Clientes, OT (listado y seguimiento).

### 2.3 Clientes (listado)

```text
┌───────────────────────────────────────┐
│ Clientes                [ + Nuevo ]     │
│─────────────────────────────────────────│
│ [ Buscar...              ]              │
│─────────────────────────────────────────│
│ Supermercados Norte        Activo       │
│ Edificio Rivadavia 450      Activo       │
│ Cámaras del Sur             Inactivo    │
└───────────────────────────────────────┘
```
- **Propósito:** administrar clientes del tenant.
- **Información principal:** nombre, estado.
- **Acciones principales:** buscar, crear cliente, abrir cliente.
- **Navegación:** tap en fila → Cliente / ubicaciones / activos.

### 2.4 Cliente / ubicaciones / activos

```text
┌───────────────────────────────────────┐
│ ← Supermercados Norte      [ Editar ]  │
│─────────────────────────────────────────│
│ Tel: 351-... Email: contacto@...        │
│─────────────────────────────────────────│
│ Ubicaciones               [ + Nueva ]   │
│  Sucursal Centro                        │
│    Activos: Cámara 01, Cámara 02, A/A   │
│  Depósito                                │
│    Activos: Rooftop 01                  │
└───────────────────────────────────────┘
```
- **Propósito:** vista jerárquica del cliente completo (modelo-funcional §4), base para crear una OT.
- **Información principal:** datos del cliente, ubicaciones y activos de cada una.
- **Acciones principales:** editar cliente, agregar ubicación, agregar activo, crear OT sobre un activo puntual.
- **Navegación:** tap en un activo → detalle mínimo de activo (datos + botón "Nueva OT" precargando cliente/ubicación/activo). ← vuelve a Clientes.

### 2.5 Nueva OT

```text
┌───────────────────────────────────────┐
│ Nueva Orden de Trabajo                  │
│─────────────────────────────────────────│
│ Cliente:   [ Supermercados Norte  ▾]   │
│ Ubicación: [ Sucursal Centro      ▾]   │
│ Activo:    [ Cámara frigorífica 01▾]   │
│ Tipo:      [ Correctivo           ▾]   │
│ Prioridad: [ Normal               ▾]   │
│ Descripción:                             │
│ [                                    ]  │
│                                          │
│         [ Guardar ]  [ Guardar y asignar ]│
└───────────────────────────────────────┘
```
- **Propósito:** crear una OT (modelo-funcional §7).
- **Información principal:** selección en cascada cliente → ubicación → activo, tipo, prioridad, descripción solicitada.
- **Acciones principales:** guardar (queda pendiente sin técnico); guardar y asignar (pasa directo a Asignación de técnico).
- **Navegación:** desde Clientes/Activo (precargado) o desde el menú OT (formulario vacío). Al guardar → Listado y seguimiento de OT o Asignación de técnico.

### 2.6 Asignación de técnico

```text
┌───────────────────────────────────────┐
│ Asignar técnico — OT-105                │
│─────────────────────────────────────────│
│ [ Buscar técnico...        ]            │
│─────────────────────────────────────────│
│ ○ Juan Pérez                             │
│ ○ María Gómez                            │
│─────────────────────────────────────────│
│ Fecha programada: [ __/__/____ ] (opc.) │
│                                          │
│           [ Asignar ]                   │
└───────────────────────────────────────┘
```
- **Propósito:** asignar un técnico responsable a la OT (modelo-funcional §7).
- **Información principal:** listado de técnicos del tenant.
- **Acciones principales:** seleccionar técnico, fijar fecha programada (opcional), confirmar asignación.
- **Navegación:** se accede desde Nueva OT o desde el Detalle de una OT sin asignar. Al asignar → Listado y seguimiento de OT.

### 2.7 Listado y seguimiento de OT

```text
┌───────────────────────────────────────┐
│ Órdenes de Trabajo                       │
│─────────────────────────────────────────│
│ [Estado▾][Técnico▾][Cliente▾][Fecha▾]  │
│ [ Buscar...                     ]       │
│─────────────────────────────────────────│
│ OT-105  Pendiente   Sin asignar          │
│ OT-104  En proceso  Juan Pérez           │
│ OT-101  Terminada   Juan Pérez           │
└───────────────────────────────────────┘
```
- **Propósito:** seguimiento operativo de todas las OT del tenant (PRD §44).
- **Información principal:** número, estado, técnico, y columnas de cliente/prioridad/fecha según filtro.
- **Acciones principales:** filtrar, buscar, abrir OT.
- **Navegación:** tap en fila → Detalle de OT (vista oficina, con opción de reasignar si no está cerrada) o Consulta de OT terminada si ya cerró.

### 2.8 Consulta de OT terminada

```text
┌───────────────────────────────────────┐
│ ← OT-101                Terminada       │
│─────────────────────────────────────────│
│ Cliente/Ubicación/Activo                │
│ Técnico: Juan Pérez                     │
│ Solicitado / Realizado                  │
│ Fotos (2)                               │
│─────────────────────────────────────────│
│ Historial                                │
│  - Creada (oficina)                      │
│  - Asignada a Juan Pérez                │
│  - Iniciada / Finalizada                 │
│─────────────────────────────────────────│
│ [ Ver comprobante ]  [ Reabrir ]        │
└───────────────────────────────────────┘
```
- **Propósito:** revisar el resultado completo de una OT cerrada, incluyendo trazabilidad (WorkOrderHistory).
- **Información principal:** todos los datos de la OT, fotos, historial de eventos.
- **Acciones principales:** ver/generar comprobante; reabrir (solo `TENANT_OFFICE`/`TENANT_ADMIN`, acción controlada — modelo-funcional §9).
- **Navegación:** ← vuelve al Listado y seguimiento.

---

## 3. Administrador del tenant

Alcance mínimo: usuarios, técnicos, parámetros básicos, configuración de la empresa. Sin planes comerciales ni permisos granulares.

### 3.1 Usuarios

```text
┌───────────────────────────────────────┐
│ Usuarios                  [ + Nuevo ]   │
│─────────────────────────────────────────│
│ Juan Pérez     Técnico       Activo     │
│ Ana López      Administrativo Activo    │
│ Carla Ruiz     Admin. empresa Activo    │
└───────────────────────────────────────┘
```
- **Propósito:** administrar cuentas de acceso del tenant (User + Role).
- **Información principal:** nombre, rol, estado.
- **Acciones principales:** crear usuario (nombre, email, rol), activar/desactivar.
- **Navegación:** acceso desde menú de administración (visible solo para `TENANT_ADMIN`).

### 3.2 Técnicos

```text
┌───────────────────────────────────────┐
│ Técnicos                  [ + Nuevo ]   │
│─────────────────────────────────────────│
│ Juan Pérez      351-...      Activo     │
│ María Gómez     351-...      Activo     │
└───────────────────────────────────────┘
```
- **Propósito:** administrar el registro de técnicos (Technician, extiende a un User con rol técnico).
- **Información principal:** nombre, teléfono, estado.
- **Acciones principales:** crear técnico (asociado a un usuario existente o creado en el mismo paso), activar/desactivar.
- **Navegación:** independiente de Usuarios pero relacionada (un alta de técnico puede crear el User subyacente en el mismo formulario).

### 3.3 Parámetros básicos

Un único patrón de pantalla, reutilizado para los cuatro catálogos parametrizables (`WorkOrderStatus`, `Priority`, `WorkOrderType`, `AssetType`):

```text
┌───────────────────────────────────────┐
│ Parámetros                              │
│ [Estados][Prioridades][Tipos de trabajo]│
│ [Tipos de activo]                       │
│─────────────────────────────────────────│
│ Estados de OT              [ + Nuevo ]  │
│  Pendiente        (interno: PENDING)     │
│  En proceso       (interno: IN_PROGRESS) │
│  Terminada        (interno: COMPLETED)   │
│  No resuelta      (interno: UNRESOLVED)  │
└───────────────────────────────────────┘
```
- **Propósito:** que el `TENANT_ADMIN` edite las etiquetas visibles de cada catálogo sin tocar código (PRD §53).
- **Información principal:** lista de valores del catálogo activo, mostrando la etiqueta editable y el código interno (de solo lectura) que le da estabilidad al comportamiento del sistema.
- **Acciones principales:** editar etiqueta visible, activar/desactivar valor, agregar valor nuevo dentro del mismo catálogo (sin tocar el código interno).
- **Navegación:** pestañas superiores cambian de catálogo dentro de la misma pantalla.

### 3.4 Configuración de la empresa

```text
┌───────────────────────────────────────┐
│ Configuración de la empresa             │
│─────────────────────────────────────────│
│ Nombre comercial: [ Serv. Técnico Cba ] │
│ Logo:  [ subir imagen ]                 │
│ Datos de contacto: [ ... ]              │
│ Datos para comprobante: [ ... ]         │
│                                          │
│              [ Guardar ]                │
└───────────────────────────────────────┘
```
- **Propósito:** editar `TenantConfig` — identidad y branding básico del tenant.
- **Información principal:** nombre comercial, logo, contacto, datos que aparecerán en el comprobante de OT.
- **Acciones principales:** editar y guardar.
- **Navegación:** acceso desde menú de administración.

---

## 4. PLATFORM_OWNER

Alcance mínimo: alta y consulta de tenants, estado del tenant. Sin facturación SaaS, planes comerciales ni administración avanzada (fuera del MVP — PRD §17).

### 4.1 Tenants (listado)

```text
┌───────────────────────────────────────┐
│ Tenants                   [ + Nuevo ]   │
│─────────────────────────────────────────│
│ Servicio Técnico Córdoba    Activo       │
│ Ascensores del Litoral      Activo       │
│ Plagas Sur                  Suspendido   │
└───────────────────────────────────────┘
```
- **Propósito:** que la plataforma vea todas las empresas dadas de alta.
- **Información principal:** nombre comercial del tenant, estado.
- **Acciones principales:** crear tenant, abrir tenant.
- **Navegación:** tap en fila → Detalle/estado de tenant.

### 4.2 Alta de tenant

```text
┌───────────────────────────────────────┐
│ Nuevo tenant                             │
│─────────────────────────────────────────│
│ Nombre comercial: [                  ]  │
│ Email admin. inicial: [              ]  │
│                                          │
│              [ Crear ]                  │
└───────────────────────────────────────┘
```
- **Propósito:** crear un tenant nuevo con su primer `TENANT_ADMIN`.
- **Información principal:** datos mínimos del tenant y del administrador inicial.
- **Acciones principales:** crear.
- **Navegación:** al crear → Detalle/estado de tenant.

### 4.3 Detalle/estado de tenant

```text
┌───────────────────────────────────────┐
│ ← Servicio Técnico Córdoba              │
│─────────────────────────────────────────│
│ Estado: Activo      [ Suspender ]       │
│ Admin. inicial: Carla Ruiz              │
│ Fecha de alta: 03/2026                  │
└───────────────────────────────────────┘
```
- **Propósito:** consultar y cambiar el estado operativo del tenant.
- **Información principal:** estado, administrador inicial, fecha de alta.
- **Acciones principales:** activar/suspender el tenant.
- **Navegación:** ← vuelve a Tenants.

---

## 5. Resumen de navegación por rol

```text
TENANT_TECHNICIAN
  Login → Mis OT → Detalle → Iniciar → Registrar (+Fotos, +Estado) → Finalizar → Mis OT

TENANT_OFFICE / TENANT_ADMIN
  Login → Inicio → {Clientes → Cliente/Ubicaciones/Activos → Nueva OT,
                     OT → Listado y seguimiento → Detalle/Consulta terminada}

TENANT_ADMIN (administración)
  Inicio → Administración → {Usuarios, Técnicos, Parámetros, Configuración de la empresa}

PLATFORM_OWNER
  Login → Tenants → {Alta de tenant, Detalle/estado de tenant}
```

---

## 6. Fuera de alcance de estos wireframes

Conforme a PRD §58: firma del cliente, portal de clientes, optimización de rutas/GPS, facturación electrónica, planes comerciales, permisos granulares, inventario, presupuestos y contratos no tienen pantalla en esta versión.
