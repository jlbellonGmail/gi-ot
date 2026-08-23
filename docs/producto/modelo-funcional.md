# Modelo funcional v0.1 — gi-ot

**Estado:** BOOTSTRAP
**Fuente de verdad funcional:** `docs/producto/PRD.md`
**Documento:** `docs/producto/modelo-funcional.md`

Este documento no repite el PRD. Traduce sus principios en el modelo operativo concreto que guiará la construcción del MVP: quién opera el sistema, con qué entidades, en qué orden, y cómo se mueve una Orden de Trabajo desde que nace hasta que queda archivada en el historial de un activo.

---

## 1. La plataforma como estructura de tres niveles

```text
PLATAFORMA gi-ot
      │
      ├── PLATFORM_OWNER (opera la plataforma, no un tenant)
      │
      └── TENANT (empresa cliente)
             │
             ├── configuración propia
             ├── usuarios propios
             ├── clientes propios
             └── Órdenes de Trabajo propias
```

Un usuario existe siempre dentro de exactamente un tenant, con la única excepción de `PLATFORM_OWNER`, que existe a nivel plataforma y no pertenece a ningún tenant. Ningún dato de negocio (cliente, ubicación, activo, OT) existe fuera de un tenant.

---

## 2. Tenant

El Tenant es la empresa que contrata gi-ot y la frontera de aislamiento de todo el sistema.

Todo lo que un tenant ve, crea o modifica queda contenido dentro de su propio espacio. Un tenant nunca sabe que existen otros tenants.

Cada tenant tiene:

* identidad básica (nombre comercial, datos de contacto);
* su propia configuración (`TenantConfig`): estados de OT, prioridades, tipos de activo, tipos de trabajo, motivos, etiquetas visibles, branding básico;
* sus propios usuarios, técnicos, clientes, ubicaciones, activos y OT.

La configuración de un tenant nunca afecta a otro. El rubro de la empresa (climatización, ascensores, plagas, etc.) se expresa completamente mediante esta configuración, nunca mediante código distinto.

---

## 3. Usuarios y roles

Cuatro roles, dos alcances:

```text
Alcance PLATAFORMA
  └── PLATFORM_OWNER

Alcance TENANT
  ├── TENANT_ADMIN
  ├── TENANT_OFFICE
  └── TENANT_TECHNICIAN
```

**PLATFORM_OWNER** — administra la plataforma en su conjunto: altas de tenants, habilitación/suspensión, planes. Fuera del alcance operativo del MVP salvo lo mínimo para poder crear el primer tenant.

**TENANT_ADMIN** — el máximo nivel dentro de la empresa. Administra usuarios, técnicos, configuración, y tiene acceso a todo lo que un `TENANT_OFFICE` puede hacer.

**TENANT_OFFICE** — personal administrativo. Gestiona clientes, ubicaciones, activos, crea y asigna OT, hace seguimiento y consulta historial. No administra usuarios ni configuración del tenant.

**TENANT_TECHNICIAN** — ejecuta trabajo en campo. Ve y opera sus propias OT asignadas, puede crear una OT urgente, y trabaja predominantemente desde el celular, incluso sin conexión.

Los nombres visibles de estos roles podrán parametrizarse por tenant, pero la capacidad interna asociada a cada rol es fija durante el MVP: no existe todavía un sistema de permisos granulares ni roles a medida.

---

## 4. Jerarquía comercial: Cliente → Ubicación → Activo

```text
Tenant
  └── Customer
        └── Location
              └── Asset
```

* **Customer** (Cliente) — quien recibe el servicio (persona u organización). Puede tener una o varias `Location`.
* **Location** — un lugar físico del cliente (sucursal, planta, depósito, domicilio).
* **Asset** — el elemento sobre el que se interviene, normalmente asociado a una `Location`. Su `AssetType` (split, ascensor, cámara frigorífica, etc.) es configuración de tenant, no una lista fija del producto.

Un activo puede crearse con datos mínimos (solo un nombre); todo lo demás — marca, modelo, número de serie, QR — es opcional y se completa progresivamente.

`Customer` no guarda por sí mismo nombre, dirección, teléfono ni email: esos datos generales viven en `Person`, la base compartida detrás de Cliente y Técnico (§4bis, `docs/tecnica/modelo-datos.md` §10). Esto es una abstracción interna — quien opera el sistema sigue pensando y trabajando en términos de "Cliente".

---

## 4bis. Person: una sola persona, varias funciones

Una misma persona real puede participar de más de una función dentro del mismo tenant — por ejemplo, ser Cliente y Técnico a la vez. Para no duplicar sus datos generales en cada función, el modelo interno separa:

```text
Person                    (datos generales: una sola vez por tenant)
 │
 ├── Customer              (especialización: rol comercial de cliente)
 └── Technician             (especialización: rol operativo de técnico)
```

Esto es completamente transparente para quien usa el sistema: la interfaz nunca pide "crear una Persona"; se opera siempre desde el concepto de negocio correspondiente.

**Alta de Cliente:**

```text
Clientes → Nuevo Cliente
  ↓ tipo de persona, país, tipo y número de identificación
  ↓ el sistema busca esa identificación dentro del tenant
  ├── no existe  → crea Cliente en una sola acción (por dentro: Person +
  │                identificación + Customer)
  └── ya existe  → muestra sus datos generales, permite actualizarlos,
                    y agrega la función de Cliente si todavía no la tenía
                    (si ya era Cliente, informa que ya está registrado)
```

**Alta de Técnico** sigue exactamente el mismo patrón desde `Técnicos → Nuevo Técnico`.

Si los datos generales (teléfono, dirección, email) se actualizan desde la ficha de Técnico, ese cambio se refleja de inmediato al consultar a esa misma persona como Cliente, y viceversa — es la misma información, en un solo lugar.

Detalle técnico completo (claves, restricciones, transaccionalidad, prevención de duplicados, extensión futura a Proveedor/Socio/etc.): `docs/tecnica/modelo-datos.md` §10.

---

## 5. Técnicos

`Technician` (§4bis) es la especialización de `Person` para el rol operativo de campo. Ejecuta OT, no administra el tenant. En el MVP, una OT tiene un único técnico responsable — no hay cuadrillas ni colaboradores múltiples todavía.

`Technician` es independiente de tener o no un `User` de acceso al sistema: una persona puede estar registrada como técnico sin necesariamente disponer de credenciales de acceso, y un `User` con rol de seguridad `TENANT_TECHNICIAN` no implica automáticamente una fila `Technician` (no confundir especialización de negocio con rol RBAC — `docs/tecnica/modelo-datos.md` §10.9).

---

## 6. La Orden de Trabajo (OT)

Entidad central del sistema. Une en un solo registro quién pidió el trabajo, sobre qué activo, quién lo ejecuta, qué se hizo y con qué evidencia.

```text
WorkOrder
  ├── Tenant           (frontera de aislamiento)
  ├── Customer
  ├── Location
  ├── Asset
  ├── Technician        (responsable principal)
  ├── WorkOrderType      (correctivo, preventivo, instalación, ...)
  ├── Priority           (baja, normal, alta, urgente)
  ├── WorkOrderStatus    (pendiente, en proceso, terminada, no resuelta)
  ├── descripción solicitada / trabajo realizado
  ├── fechas (programada, inicio, fin, creación, modificación)
  ├── WorkOrderPhoto[]
  └── WorkOrderHistory[]
```

En el MVP, una OT está asociada a un único activo. Si una visita cubre varios activos, se generan varias OT relacionadas — no existe todavía el concepto de "visita" como agrupador.

`WorkOrderStatus`, `Priority` y `WorkOrderType` son catálogos parametrizables por tenant, con una semántica interna estable (p. ej. `PENDING`, `IN_PROGRESS`, `COMPLETED`, `UNRESOLVED`) independiente de la etiqueta visible que cada tenant configure.

---

## 7. Flujo Oficina

```text
Crear
  ↓ selecciona Cliente → Ubicación → Activo
  ↓ describe el trabajo, fija tipo y prioridad
Asignar
  ↓ selecciona Technician
  ↓ programa fecha (opcional)
Seguir
  ↓ consulta estado, filtra por técnico/cliente/estado/fecha
Consultar
  ↓ ve historial, comprobante, resultado
```

Oficina (`TENANT_OFFICE` o `TENANT_ADMIN`) es responsable de crear y asignar la OT, y de hacer seguimiento hasta el cierre. También puede reabrir una OT terminada, de forma controlada y trazable — un técnico no puede hacerlo por sí mismo.

---

## 8. Flujo Técnico

```text
Recibir
  ↓ ve la OT asignada (en línea u offline si ya sincronizó)
Iniciar
  ↓ marca inicio de trabajo
Ejecutar
  ↓ realiza el trabajo en campo
Registrar
  ↓ describe lo realizado (texto o dictado por voz), adjunta fotos
Cerrar
  ↓ cambia estado a terminada / no resuelta
```

El técnico también puede iniciar el flujo de urgencia, creando una OT nueva directamente en campo sin depender de que Oficina la haya generado antes — típicamente cuando descubre un problema adicional durante una visita.

Este flujo debe poder ejecutarse íntegramente sin conexión: abrir, registrar, fotografiar y cerrar quedan disponibles en local y se sincronizan cuando vuelve la red.

---

## 9. Ciclo de vida de la OT

```text
        (Oficina crea)              (Técnico crea, urgencia)
              │                              │
              └──────────────┬───────────────┘
                              ▼
                          PENDIENTE
                              │
                     (técnico inicia)
                              ▼
                         EN PROCESO
                              │
                 (técnico registra y finaliza)
                    ┌─────────┴─────────┐
                    ▼                   ▼
               TERMINADA           NO RESUELTA
                    │                   │
                    └─────────┬─────────┘
                     (reapertura controlada,
                      solo Oficina/Admin)
                              ▼
                          PENDIENTE
```

Una OT terminada no es editable libremente: solo una reapertura explícita y trazable (registrada en `WorkOrderHistory`) permite volver a modificarla. Todo cambio relevante de estado queda registrado con usuario y fecha.

---

## 10. Del cierre al historial

Al cerrar una OT:

1. queda disponible el comprobante de trabajo (datos de empresa, OT, cliente, activo, técnico, resultado);
2. puede dispararse una notificación al cliente (email como canal inicial);
3. el evento se agrega al historial del `Asset` y al del `Customer`.

```text
Asset
  └── historial de intervenciones (todas las OT cerradas sobre ese activo)

Customer
  └── Locations → Assets → OT (historial completo de servicio)
```

Este historial es uno de los valores centrales del producto: permite responder, para cualquier activo, "qué se le hizo y cuándo" sin depender de memoria ni papeles sueltos.

---

## 11. Relación entre parametrización y funcionamiento

Todo lo que varía entre rubros (tipos de activo, tipos de trabajo, estados, prioridades, motivos) se resuelve mediante `TenantConfig`, nunca mediante ramas de código o instalaciones distintas del producto. El modelo funcional descrito arriba es el mismo para una empresa de climatización, de ascensores o de control de plagas — solo cambian las etiquetas y catálogos configurados por tenant.

---

## 12. Fuera de este modelo (ver PRD §58)

Facturación, cobranzas, inventario real, optimización de rutas, portal de clientes, CRM completo y BI avanzado no forman parte de este modelo funcional inicial. Se incorporarán como módulos futuros sin alterar el núcleo aquí descrito.
