# SPEC: activar-ai-native

## Contexto
- **PRD**: N/A (transición de gobierno)
- **ROADMAP**: Punto 12 — Activación AI-NATIVE / SDD
- **Problema**: Transicionar gi-ot de modo BOOTSTRAP a AI-NATIVE activando el circuito formal de desarrollo asistido por IA para todas las features futuras.

## Alcance
### Incluye
- [ ] Actualizar AGENTS.md: BOOTSTRAP → AI-NATIVE
- [ ] Crear `.agentic/` con circuito formal (circuit.md, roles, workflows, templates, hitl.md)
- [ ] Configurar GitHub Actions CI (`.github/workflows/ci.yml`)
- [ ] Crear spec.md para esta feature en `runs/activar-ai-native/`
- [ ] Validar que develop sigue limpio y sincronizado

### No incluye (fuera de scope)
- [ ] Implementar Punto 10 (Validación PostgreSQL)
- [ ] Cambios funcionales al producto
- [ ] Modificaciones a tests existentes
- [ ] Cambios en documentación de producto (PRD, arquitectura, modelo-datos)

## Comportamiento
### Reglas funcionales específicas
1. A partir de esta activación, toda nueva feature/milestone DEBE usar el circuito AI-NATIVE
2. Git strategy: feature branches + PR + HITL obligatorio
3. CI/CD automático en PR hacia develop/main
4. Evidencias en `runs/<feature>/` para cada feature
5. `spec.md` como contrato inmutable

### Excepciones justificadas
- El histórico BOOTSTRAP (Puntos 00-09) se conserva tal cual
- No se reescribe ni rebasea historia previa
- La transición es solo de gobierno/circuito, no de código funcional

## Interfaces afectadas
### API Endpoints
| Método | Path | Descripción |
|--------|------|-------------|
| N/A | N/A | Sin cambios funcionales |

### UI Components
| Componente | Ruta | Descripción |
|------------|------|-------------|
| N/A | N/A | Sin cambios funcionales |

### DB Schema
| Tabla | Cambio | Migración |
|-------|--------|-----------|
| N/A | N/A | Sin migraciones |

## Datos
### Modelos nuevos/modificados
- N/A

### Migraciones requeridas
- N/A

## Seguridad
### Multitenancy
- Sin cambios — reglas existentes se mantienen

### Permisos (RBAC)
- Sin cambios — roles existentes se mantienen

### Validaciones
- Sin cambios funcionales

## Tests requeridos
### Unitarios
- N/A (transición de gobierno)

### Integración
- [ ] Verificar que suite completa (106 tests) pasa
- [ ] Verificar que CI GitHub Actions ejecuta correctamente

### E2E/UI
- N/A

## Criterios de aceptación
- [ ] AGENTS.md actualizado a AI-NATIVE con histórico BOOTSTRAP preservado
- [ ] `.agentic/` creado con: circuit.md, roles/, workflows/git.md, templates/spec.md, hitl.md
- [ ] `.github/workflows/ci.yml` creado y funcional
- [ ] `runs/activar-ai-native/spec.md` creado (este archivo)
- [ ] Working tree limpio en branch `feature/activar-ai-native`
- [ ] Suite completa 106 tests pasa localmente
- [ ] SHA HEAD = SHA origin/develop antes de crear PR
- [ ] PR creado hacia develop con checks CI pendientes/verdes

## Referencias transversales
- `.agentic/circuit.md` — Circuito completo
- `.agentic/roles/` — Analyst, Reviewer, Builder, QA, Code Reviewer
- `.agentic/workflows/git.md` — Estrategia Git formal
- `.agentic/templates/spec.md` — Template de specs
- `.agentic/hitl.md` — Proceso HITL
- `.github/workflows/ci.yml` — CI/CD
- `docs/ui-ux/UI-UX-STANDARDS.md` — Para features futuras con UI
- `docs/tecnica/arquitectura.md` — Arquitectura actual
- `docs/tecnica/modelo-datos.md` — Modelo de datos
- `docs/tecnica/stack.md` — Stack actual
- `docs/producto/PRD.md` — Producto
- `ROADMAP.md` — Punto 12 activado

---

## Checklist pre-Analyst
- [x] Problema claro: activar circuito AI-NATIVE
- [x] Alcance acotado: solo gobierno/circuito
- [x] Dependencias: ninguna (infraestructura only)
- [x] Riesgos: bajo (no toca código funcional)

## Checklist pre-Reviewer
- [x] Spec completo
- [x] Referencias transversales correctas
- [x] No duplica docs transversales
- [x] Criterios de aceptación verificables

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