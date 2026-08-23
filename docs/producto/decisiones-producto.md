# Decisiones de producto — gi-ot

**Estado:** BOOTSTRAP
**Documento:** `docs/producto/decisiones-producto.md`

Registro canónico y breve de las decisiones estructurales ya adoptadas durante la Etapa 00. No reexplica ni duplica `PRD.md`, `stack.md` ni `arquitectura.md` — remite a ellos como fuente de detalle.

---

## 1. SaaS multitenant desde el inicio

- **Decisión:** gi-ot es una plataforma SaaS multitenant desde su primera versión funcional.
- **Motivo:** el producto nace para servir a múltiples empresas sobre una base común (PRD §5).
- **Consecuencia:** ninguna entidad de negocio puede diseñarse asumiendo una única empresa.

## 2. Un único producto compartido

- **Decisión:** existe una sola aplicación y una sola API para todos los tenants; no se construyen forks por cliente.
- **Motivo:** sostener un producto mantenible y escalable comercialmente (PRD §4).
- **Consecuencia:** las diferencias entre empresas se resuelven en configuración, no en código separado.

## 3. Parametrización antes que personalización por código

- **Decisión:** ante una necesidad de un cliente, se evalúa primero si se resuelve mediante parámetro.
- **Motivo:** evitar la proliferación de variantes del producto (PRD §68).
- **Consecuencia:** el desarrollo a medida es la excepción, no la regla.

## 4. Roles base

- **Decisión:** cuatro roles iniciales: `PLATFORM_OWNER`, `TENANT_ADMIN`, `TENANT_OFFICE`, `TENANT_TECHNICIAN`.
- **Motivo:** cubren los perfiles mínimos necesarios para operar el MVP (PRD §16).
- **Consecuencia:** el RBAC del MVP no contempla roles personalizados ni permisos granulares.

## 5. Mobile-first mediante PWA

- **Decisión:** el frontend es una única aplicación Next.js/PWA, priorizada para uso móvil.
- **Motivo:** el técnico de campo es el usuario más frecuente del sistema (PRD §34, §61).
- **Consecuencia:** no se desarrolla app nativa salvo necesidad demostrada.

## 6. Offline como requisito funcional

- **Decisión:** el flujo técnico debe operar sin conexión, con sincronización posterior.
- **Motivo:** la conectividad en campo no está garantizada (PRD §39).
- **Consecuencia:** toda funcionalidad móvil relevante se diseña considerando datos locales y cola de sincronización.

## 7. Una OT con un técnico responsable principal

- **Decisión:** cada Orden de Trabajo tiene un único técnico responsable en el MVP.
- **Motivo:** mantener simple la ejecución y reducir conflictos de edición concurrente (PRD §42, §50).
- **Consecuencia:** cuadrillas y múltiples responsables quedan para una evolución posterior.

## 8. Una OT asociada principalmente a un activo

- **Decisión:** cada OT se vincula a un único activo.
- **Motivo:** mantener un historial simple y preciso por activo (PRD §51).
- **Consecuencia:** una visita con varios activos genera varias OT relacionadas; no existe agrupador de "visita" en el MVP.

## 9. SQLite exclusivamente para BOOTSTRAP local

- **Decisión:** SQLite se usa solo como facilidad de desarrollo local.
- **Motivo:** simplicidad y costo cero durante BOOTSTRAP (stack.md).
- **Consecuencia:** SQLite nunca es la base de producción ni condiciona el diseño del dominio.

## 10. PostgreSQL como persistencia objetivo de producción

- **Decisión:** PostgreSQL es el motor de base de datos de producción.
- **Motivo:** soporta el volumen, la concurrencia y RLS que requiere el producto en producción (stack.md).
- **Consecuencia:** el modelo de datos se diseña desde el inicio compatible con ambos motores (modelo-datos.md §6).

## 11. `tenant_id` desde el modelo inicial

- **Decisión:** toda entidad de negocio incluye `tenant_id` desde el primer modelo de datos.
- **Motivo:** el tenant es la frontera de seguridad del sistema (PRD §6, arquitectura.md §3).
- **Consecuencia:** ninguna tabla de negocio ni consulta puede omitir el filtrado por tenant.

## 12. RLS como defensa adicional, no sustituto

- **Decisión:** Row-Level Security en PostgreSQL refuerza el aislamiento, pero no reemplaza la autorización y el filtrado explícito en el backend.
- **Motivo:** SQLite no soporta RLS y la lógica de negocio ya debe garantizar el aislamiento por sí sola (arquitectura.md §3.4).
- **Consecuencia:** el filtrado por `tenant_id` en la capa de aplicación es obligatorio incluso cuando RLS esté activo.

## 13. Monolito modular para el MVP

- **Decisión:** la API se construye como un monolito modular (`apps/api`), no como microservicios.
- **Motivo:** evitar complejidad operativa prematura durante el MVP (stack.md, arquitectura.md §2).
- **Consecuencia:** los módulos internos se comunican en proceso; los futuros módulos del ecosistema seguirán el mismo patrón.

## 14. Sin infraestructura adicional sin necesidad demostrada

- **Decisión:** no se incorporan microservicios, Kubernetes, Redis, brokers de mensajería, GraphQL, CQRS ni event sourcing salvo necesidad demostrada.
- **Motivo:** mantener mínima la complejidad operativa durante BOOTSTRAP y el MVP (AGENTS.md, stack.md).
- **Consecuencia:** cualquier incorporación futura de estas piezas requiere decisión explícita y actualización de `stack.md`.

## 15. Fotografías: filesystem local en BOOTSTRAP, Object Storage en producción

- **Decisión:** las fotos de OT se almacenan en `data/uploads/` durante BOOTSTRAP y en Object Storage S3-compatible en producción.
- **Motivo:** simplicidad local sin dependencias externas, con ruta clara de escalado (stack.md, arquitectura.md §7).
- **Consecuencia:** la base de datos solo guarda metadatos y referencia, nunca el binario, en ambos entornos.

## 16. Person como base compartida detrás de Cliente y Técnico

- **Decisión:** `Customer` (Cliente) y `Technician` (Técnico) no son entidades independientes; son especializaciones de una entidad base `Person`, con clave compuesta `(tenant_id, person_id)`. Los datos generales (nombre, dirección, teléfono, email) viven únicamente en `Person`.
- **Motivo:** una misma persona real puede cumplir más de una función dentro de la misma empresa (p. ej. ser cliente y técnico a la vez); duplicar sus datos generales por función generaría inconsistencia y trabajo doble de mantenimiento (modelo-datos.md §10).
- **Consecuencia:** el alta de Cliente o Técnico busca primero por identificación (`PersonIdentification`) dentro del tenant y reutiliza la `Person` existente si la encuentra; el usuario nunca opera directamente sobre `Person`, solo sobre los conceptos de negocio "Cliente" y "Técnico". El patrón queda preparado para futuras especializaciones (Proveedor, Socio, etc.) sin modificar `Person`, aunque no se implementan todavía. Esta especialización de negocio es un concepto independiente de los roles RBAC (decisión 4).

## 17. Evolución del proyecto

- **Decisión:** el proyecto avanza según la secuencia `PRD → ROADMAP → BOOTSTRAP → MVP vertical → SDD → AI-NATIVE`.
- **Motivo:** construir rápido una base correcta antes de activar el circuito agéntico formal (AGENTS.md, PRD §69-§71).
- **Consecuencia:** la activación de SDD/AI-NATIVE requiere decisión explícita del usuario y no implica reescribir la aplicación.

---

## Fuentes

`docs/producto/PRD.md` · `docs/tecnica/stack.md` · `docs/tecnica/arquitectura.md` · `docs/tecnica/modelo-datos.md` · `AGENTS.md`
