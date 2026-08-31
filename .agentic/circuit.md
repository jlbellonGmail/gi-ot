# Circuito AI-NATIVE — gi-ot

## Visión general

Este documento define el circuito formal de desarrollo asistido por IA para gi-ot.
Está basado en el template estándar de opencode y adaptado al stack/producto de gi-ot.

El circuito se compone de **5 roles agénticos** + **HITL** (Human-In-The-Loop).

---

## Roles del circuito

| Rol | Responsabilidad principal | Entrada | Salida |
|-----|---------------------------|---------|--------|
| **Analyst** | Análisis de requisitos, viabilidad, descomposición en tasks | Feature request / spec draft | `runs/<feature>/analysis.md` |
| **Reviewer** | Revisión de análisis, arquitectura, seguridad, compliance | `analysis.md` | `review.md` (APROBADO / RECHAZADO / CAMBIOS) |
| **Builder** | Implementación de código, tests, documentación | `analysis.md` + `review.md` (APROBADO) | Código + tests + `build.md` |
| **QA** | Validación funcional, integración, regresión, performance | Código + `build.md` | `qa.md` (PASS / FAIL) |
| **Code Reviewer** | Revisión de calidad de código, estilo, seguridad, mantenibilidad | Código + `build.md` | `codereview.md` (APROBADO / CAMBIOS) |

---

## Flujo obligatorio

```
Feature Request
       │
       ▼
   ┌─────────┐
   │ Analyst │ ◄── Crea runs/<feature>/spec.md + analysis.md
   └────┬────┘
        │
        ▼
   ┌──────────┐
   │ Reviewer │ ◄── Valida análisis, arquitectura, seguridad
   └────┬─────┘
        │
        ▼ (APROBADO)
   ┌─────────┐
   │ Builder │ ◄── Implementa, tests, docs
   └────┬────┘
        │
        ▼
   ┌────┐
   │ QA │ ◄── Valida funcional, integración, regresión
   └──┬─┘
        │
        ▼ (PASS)
   ┌──────────────┐
   │Code Reviewer │ ◄── Revisión final de calidad
   └──────┬───────┘
          │
          ▼ (APROBADO)
   ┌─────────┐
   │  HITL   │ ◄── Aprobación humana para merge
   └────┬────┘
        │
        ▼ (MERGE)
   Merge a develop
```

---

## Gates obligatorios

### Gate 1: Post-Analyst (Reviewer)
- `analysis.md` completo y coherente
- `spec.md` referencia documentos transversales (no los duplica)
- Viabilidad técnica confirmada
- Riesgos identificados

### Gate 2: Post-Reviewer
- Reviewer emite `review.md` con estado: **APROBADO** | **RECHAZADO** | **CAMBIOS REQUERIDOS**
- Solo **APROBADO** permite continuar a Builder

### Gate 3: Post-Builder (QA)
- Tests unitarios + integración pasando localmente
- Lint/format/typecheck/build sin errores
- `build.md` documenta cambios y decisiones

### Gate 4: Post-QA
- QA emite `qa.md` con estado: **PASS** | **FAIL**
- Suite completa del producto ejecutada
- Tests de la feature validados
- Regresiones verificadas

### Gate 5: Post-Code Reviewer
- Code Reviewer emite `codereview.md` con estado: **APROBADO** | **CAMBIOS REQUERIDOS**
- Calidad de código, seguridad, mantenibilidad validadas

### Gate 6: HITL (Pre-merge)
- Humano autoriza **MERGE** o **NO MERGE**
- Evidencia real de todos los gates previos

---

## Artefactos por feature

Estructura obligatoria en `runs/<feature>/`:

```
runs/<feature>/
├── spec.md           # Especificación formal (inmutable tras aprobación)
├── analysis.md       # Análisis del Analyst
├── review.md         # Revisión del Reviewer
├── build.md          # Registro de implementación del Builder
├── qa.md             # Validación de QA
├── codereview.md     # Revisión de Code Reviewer
├── hitl.md           # Registro de decisión humana
└── evidence/         # Evidencias (logs, screenshots, reports)
```

### spec.md — Contrato mínimo

```markdown
# SPEC: <feature-name>

## Contexto
- Referencia a PRD/ROADMAP
- Problema a resolver

## Alcance
- Incluye / No incluye

## Comportamiento
- Reglas funcionales específicas
- Excepciones justificadas

## Interfaces afectadas
- API endpoints
- UI components
- DB schema

## Datos
- Modelos nuevos/modificados
- Migraciones

## Seguridad
- Multitenancy
- Permisos
- Validaciones

## Tests requeridos
- Unitarios
- Integración
- E2E/UI si aplica

## Criterios de aceptación
- Lista verificable

## Referencias transversales
- docs/ui-ux/UI-UX-STANDARDS.md
- docs/tecnica/arquitectura.md
- docs/tecnica/modelo-datos.md
- AGENTS.md
```

---

## Reglas Git (AI-NATIVE)

### Ramas
- `main` — Solo releases/versiones (protegida)
- `develop` — Rama de integración (protegida, solo merge via PR)
- `feature/<nombre>` — Una por feature/milestone
- `hotfix/<nombre>` — Solo para correcciones críticas en main

### Workflow
1. Crear `feature/<nombre>` desde `develop`
2. Trabajo completo en la rama (commits atómicos, mensajes en español)
3. Push de la rama
4. Crear PR hacia `develop`
5. CI ejecuta validaciones automáticas
6. Circuit agents ejecutan sus roles (evidencia en `runs/`)
7. HITL autoriza merge
8. Merge squash a `develop`
9. Delete feature branch

### Prohibido
- Commit directo a `develop` o `main`
- Force push a ramas protegidas
- Merge sin PR
- Merge sin checks verdes
- Rebase de `develop` sobre feature

---

## CI/CD (GitHub Actions)

### Workflows obligatorios
- `ci.yml` — Ejecuta en PR hacia develop/main
  - Lint/format/typecheck
  - Tests backend (pytest)
  - Tests frontend (si aplica)
  - Build
  - Migraciones (dry-run)
- `release.yml` — Tag/push a main

### Required checks (branch protection)
- `ci/lint`
- `ci/tests-backend`
- `ci/tests-frontend` (si aplica)
- `ci/build`

---

## HITL (Human-In-The-Loop)

### Cuándo
- Antes de merge a develop (Gate 6)
- Antes de release a main
- Decisiones de arquitectura irreversibles

### Formato `hitl.md`
```markdown
# HITL: <feature-name>

## Decisión
- [ ] MERGE
- [ ] NO MERGE

## Autor
- Nombre: <nombre>
- Rol: <rol>
- Fecha: <ISO 8601>

## Evidencia revisada
- [ ] analysis.md
- [ ] review.md (APROBADO)
- [ ] build.md
- [ ] qa.md (PASS)
- [ ] codereview.md (APROBADO)
- [ ] CI verde en PR

## Observaciones
<texto libre>
```

---

## Adaptaciones gi-ot

### Stack específico
- Backend: FastAPI + SQLAlchemy + Alembic (Python)
- Frontend: Next.js + React + TypeScript (PWA)
- DB: SQLite (dev) → PostgreSQL (prod)
- Tests: pytest (backend), jest/playwright (frontend)

### Quality gates locales
```bash
# Backend
cd apps/api
pip install -r requirements.txt
ruff check .        # lint
mypy .              # typecheck
pytest -q           # tests
alembic upgrade head  # migraciones

# Frontend
cd apps/web
npm ci
npm run lint        # eslint
npm run typecheck   # tsc
npm run build       # build
```

### Documentos transversales de referencia
- `docs/ui-ux/UI-UX-STANDARDS.md` — Obligatorio para toda SPEC con UI
- `docs/tecnica/arquitectura.md`
- `docs/tecnica/modelo-datos.md`
- `docs/tecnica/stack.md`
- `docs/producto/PRD.md`
- `ROADMAP.md`
- `AGENTS.md`

---

## Versionado del circuito

Este circuito está versionado según el template opencode vigente.
Cambios al circuito requieren:
1. Issue/PR documentando el cambio
2. Aprobación del propietario del proyecto
3. Migración de features en curso si aplica

---

*Última actualización: 2026-08-30*
*Basado en template opencode AI-NATIVE v1.x*