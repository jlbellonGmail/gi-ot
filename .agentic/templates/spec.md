# Spec Template — gi-ot

## Uso
Copiar este archivo a `runs/<feature>/spec.md` y completar.
**No eliminar secciones** — marcar "N/A" si no aplica.

---

# SPEC: <feature-name>

## Contexto
- **PRD**: <sección/ref>
- **ROADMAP**: <punto/ref>
- **Problema**: <qué resuelve esta feature>

## Alcance
### Incluye
- [ ] Item 1
- [ ] Item 2

### No incluye (fuera de scope)
- [ ] Item 1
- [ ] Item 2

## Comportamiento
### Reglas funcionales específicas
1. Regla 1
2. Regla 2

### Excepciones justificadas
- Excepción 1: <justificación>

## Interfaces afectadas
### API Endpoints
| Método | Path | Descripción |
|--------|------|-------------|
| POST   | /api/v1/... | ... |
| GET    | /api/v1/... | ... |

### UI Components
| Componente | Ruta | Descripción |
|------------|------|-------------|
| ComponenteX | `src/app/...` | ... |

### DB Schema
| Tabla | Cambio | Migración |
|-------|--------|-----------|
| tabla_x | nueva columna | `alembic/versions/...` |

## Datos
### Modelos nuevos/modificados
- `ModelX` — <descripción>

### Migraciones requeridas
- `alembic revision --autogenerate -m "descripcion"`

## Seguridad
### Multitenancy
- Validación tenant en: <endpoints/servicios>
- Aislamiento verificado en tests

### Permisos (RBAC)
| Endpoint | Roles permitidos |
|----------|------------------|
| POST /... | TENANT_ADMIN, TENANT_OFFICE |
| GET /... | TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN |

### Validaciones
- Input sanitization: <dónde>
- Rate limiting: <si aplica>

## Tests requeridos
### Unitarios
- [ ] Servicio X: <qué testa>
- [ ] Utilidad Y: <qué testa>

### Integración
- [ ] Endpoint POST /...: <flujo>
- [ ] Endpoint GET /...: <flujo>
- [ ] Multitenancy aislamiento: <sí>
- [ ] Permisos RBAC: <sí>

### E2E/UI (si aplica)
- [ ] Flujo completo mobile: <qué>
- [ ] Flujo completo desktop: <qué>
- [ ] Accesibilidad: <qué>
- [ ] Tema claro/oscuro: <qué>

## Criterios de aceptación
- [ ] CA1: <descripción verificable>
- [ ] CA2: <descripción verificable>
- [ ] CA3: <descripción verificable>

## Referencias transversales
- `docs/ui-ux/UI-UX-STANDARDS.md` — <secciones aplicables>
- `docs/tecnica/arquitectura.md` — <secciones>
- `docs/tecnica/modelo-datos.md` — <secciones>
- `docs/tecnica/stack.md` — <secciones>
- `docs/producto/PRD.md` — <secciones>
- `ROADMAP.md` — <punto>
- `AGENTS.md` — <secciones>

---

## Checklist pre-Analyst
- [ ] Problema claro y acotado
- [ ] Alcance realista
- [ ] Dependencias identificadas
- [ ] Riesgos listados

## Checklist pre-Reviewer
- [ ] Spec completo
- [ ] Referencias transversales correctas
- [ ] No duplica docs transversales
- [ ] Criterios de aceptación verificables

## Checklist pre-Builder
- [ ] Review APROBADO
- [ ] Tasks claras en analysis.md
- [ ] Spec inmutable (no modificar)

## Checklist pre-QA
- [ ] Build.md completo
- [ ] Tests escritos
- [ ] Suite completa pasa

## Checklist pre-Code Reviewer
- [ ] QA PASS
- [ ] Código listo para revisión

## Checklist pre-HITL
- [ ] Todos los gates verdes
- [ ] Evidencia completa en runs/
- [ ] CI verde en PR