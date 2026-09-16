# HITL (Human-In-The-Loop) — gi-ot v2

El único punto de decisión humana normal es MERGE o NO MERGE sobre una PR con
evidencia vigente y CI verde. El agente no decide ni ejecuta el merge por
iniciativa propia.

## Propósito
Punto de control humano obligatorio antes de merge a `develop` y antes de release a `main`.

## Cuándo se ejecuta
1. **Pre-merge a develop** — Tras Reviewer v2 APROBADO
2. **Pre-release a main** — Tras merge a develop y validación en staging
3. **Decisiones irreversibles** — Cambios de arquitectura, migraciones destructivas, eliminación de features

## Quién autoriza
- **Pre-merge**: Product Owner / Tech Lead / Owner del proyecto
- **Pre-release**: Product Owner + Tech Lead
- **Decisiones irreversibles**: Owner del proyecto

## Proceso

### 1. Preparación (automatizada)
El sistema (CI/PR) presenta al decisor:
- Link al PR
- `runs/<feature>/spec.md`
- `runs/<feature>/analysis.md`
- `runs/<feature>/review.md` (APROBADO)
- `runs/<feature>/build.md`
- `runs/<feature>/qa.md` (PASS)
- `runs/<feature>/codereview.md` (APROBADO)
- CI checks verdes (badge/link)
- Commit SHA a mergear

### 2. Revisión humana
El decisor verifica:
- [ ] Entiende el problema y la solución
- [ ] Criterios de aceptación cumplidos (qa.md)
- [ ] Calidad de código validada (codereview.md)
- [ ] Seguridad/multitenancy OK
- [ ] No breaking changes no documentados
- [ ] Migraciones reversibles (downgrade probado)
- [ ] Docs actualizadas

### 3. Decisión
- **MERGE** / **RELEASE** — Autoriza la acción
- **NO MERGE** / **NO RELEASE** — Rechaza con justificación
- **REQUIERE CAMBIOS** — Devuelve a Builder/QA/Code Reviewer

### 4. Registro
Se crea/actualiza `runs/<feature>/hitl.md`:

```markdown
# HITL: <feature-name>

## Tipo
- [ ] Pre-merge a develop
- [ ] Pre-release a main
- [ ] Decisión irreversible

## Decisión
- [ ] MERGE / RELEASE
- [ ] NO MERGE / NO RELEASE
- [ ] REQUIERE CAMBIOS

## Autor
- Nombre: <nombre completo>
- Rol: <Product Owner / Tech Lead / Owner>
- Fecha: <ISO 8601>

## Evidencia revisada
- [ ] spec.md
- [ ] analysis.md
- [ ] review.md (APROBADO)
- [ ] build.md
- [ ] qa.md (PASS)
- [ ] codereview.md (APROBADO)
- [ ] CI checks verdes (link/badge)

## Verificaciones realizadas
- [ ] Entiendo el problema y solución
- [ ] Criterios de aceptación cumplidos
- [ ] Calidad de código validada
- [ ] Seguridad/multitenancy OK
- [ ] No breaking changes sorpresa
- [ ] Migraciones reversibles
- [ ] Documentación actualizada

## Observaciones
<texto libre: justificación, condiciones, seguimiento>

## Acción ejecutada
- Merge squash a develop: <sí/no + SHA>
- Tag release: <sí/no + versión>
- Otra: <descripción>
```

## Integración con GitHub

### Branch Protection (develop)
- Require PR reviews: 1 (Reviewer humano o responsable designado)
- Require status checks: CI passes
- Require conversation resolution: sí
- Require signed commits: opcional
- Restrict pushes: solo admins

### Required checks para merge
- `ci/lint`
- `ci/tests-backend`
- `ci/tests-frontend` (si aplica)
- `ci/build`

### Auto-merge
- **NO** habilitado — HITL humano obligatorio

## Limitaciones GitHub detectadas (gi-ot)

### Plan actual
- Repositorio: `jlbellonGmail/gi-ot`
- Plan: **Free** (repositorio privado)

### Protecciones disponibles
| Feature | Disponible (Free private) | Configurada |
|---------|---------------------------|-------------|
| Branch protection rules | **No** (solo repos públicos) | No |
| Rulesets | **No** (requiere Pro/Team/Enterprise) | No |
| Required reviews | **No** (requiere Pro/Team/Enterprise) | No |
| Required status checks | **No** (requiere Pro/Team/Enterprise) | No |
| Signed commits | **No** (requiere Pro/Team/Enterprise) | No |
| Auto-merge | **No** (requiere Pro/Team/Enterprise) | No |

### Protección actual (AI-NATIVE)
Dado que GitHub Free para repos privados no permite branch protection rules ni rulesets, la protección se logra mediante:

1. **Política AI-NATIVE documentada** (`.agentic/workflows/git.md`): prohibido commit directo a develop/main
2. **PR obligatorio por procedimiento**: todo cambio via PR desde feature branch
3. **GitHub Actions**: CI obligatorio (tests, build, quality ratchet)
4. **HITL humano antes del merge**: verificación manual antes de merge squash

### Acciones requeridas post-activación
1. Migrar a GitHub Pro/Team/Enterprise para habilitar protecciones nativas
2. Configurar branch protection en `develop` (requiere plan superior)
3. Configurar required status checks (requiere plan superior)

## Escalación
Si HITL no disponible en 24h:
- Feature simple: Tech Lead puede autorizar (documentar)
- Feature compleja: Esperar HITL formal
- Hotfix crítico: Owner autoriza con post-mortem en 48h

## Auditoría
Todos los `hitl.md` son:
- Inmutables tras creación
- Parte del historial de la feature
- Auditable en `runs/<feature>/`
