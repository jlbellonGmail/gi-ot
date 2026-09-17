# Analysis: activar-ai-native

## Resumen ejecutivo
Activación formal del circuito AI-NATIVE en gi-ot, transicionando desde el modo BOOTSTRAP histórico (Puntos 00-09) hacia el flujo gobernado por Analyst → Reviewer → Builder → QA → Code Reviewer + HITL para todas las features futuras.

## Alcance confirmado
- Incluye:
  - AGENTS.md actualizado (estado + histórico)
  - `.agentic/` directorio completo con reglas formales
  - GitHub Actions CI workflow
  - Spec template y esta feature spec
- Excluye:
  - Cambios funcionales al producto
  - Punto 10 (Validación PostgreSQL)
  - Migraciones DB
  - Tests funcionales nuevos

## Decisiones de arquitectura
- [x] Compatible con arquitectura actual (monolito modular FastAPI + Next.js)
- [x] Requiere migración DB: **no**
- [x] Requiere cambios API: **no**
- [x] Requiere cambios UI: **no**
- [x] Impacto offline: **no**
- [x] Impacto multitenancy: **no**

## Riesgos identificados
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| CI falla por configuración | Media | Alto | Validar localmente antes de push |
| GitHub branch protection no configurable (plan Free) | Alta | Medio | Documentar limitación, usar rulesets si disponible |
| Team no familiarizado con circuito | Media | Medio | Documentación completa en .agentic/ |
| HITL bottleneck | Baja | Alto | Definir escalación en hitl.md |

## Tasks para Builder
1. [x] Actualizar AGENTS.md (BOOTSTRAP → AI-NATIVE + histórico)
2. [x] Crear `.agentic/circuit.md` (visión general + gates + artefactos)
3. [x] Crear `.agentic/roles/analyst.md`
4. [x] Crear `.agentic/roles/reviewer.md`
5. [x] Crear `.agentic/roles/builder.md`
6. [x] Crear `.agentic/roles/qa.md`
7. [x] Crear `.agentic/roles/codereviewer.md`
8. [x] Crear `.agentic/workflows/git.md`
9. [x] Crear `.agentic/templates/spec.md`
10. [x] Crear `.agentic/hitl.md`
11. [x] Crear `.github/workflows/ci.yml`
12. [x] Crear `runs/activar-ai-native/spec.md` (este archivo)
13. [x] Crear `runs/activar-ai-native/analysis.md` (este archivo)

## Criterios de aceptación (heredados de spec.md)
- [x] AGENTS.md actualizado a AI-NATIVE con histórico BOOTSTRAP preservado
- [x] `.agentic/` creado con: circuit.md, roles/, workflows/git.md, templates/spec.md, hitl.md
- [x] `.github/workflows/ci.yml` creado y funcional
- [x] `runs/activar-ai-native/spec.md` creado
- [x] Working tree limpio en branch `feature/activar-ai-native`
- [ ] Suite completa 106 tests pasa localmente
- [ ] SHA HEAD = SHA origin/develop antes de crear PR
- [ ] PR creado hacia develop con checks CI pendientes/verdes

## Referencias
- PRD: N/A (transición gobierno)
- ROADMAP: Punto 12 — Activación AI-NATIVE / SDD
- Arquitectura: `docs/tecnica/arquitectura.md` (monolito modular)
- Modelo datos: `docs/tecnica/modelo-datos.md`
- UI-UX: `docs/ui-ux/UI-UX-STANDARDS.md`
- AGENTS.md: Sección "Circuito AI-NATIVE"