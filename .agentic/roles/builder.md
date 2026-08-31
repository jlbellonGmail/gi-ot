# Builder Role — gi-ot

## Propósito
Implementar la feature según `spec.md` y `analysis.md` aprobados, escribir tests, actualizar documentación y producir `build.md`.

## Entradas
- `runs/<feature>/spec.md` (APROBADO)
- `runs/<feature>/analysis.md` (APROBADO)
- `runs/<feature>/review.md` (APROBADO)
- Código base actual

## Salidas obligatorias
- Código de producción + tests
- `runs/<feature>/build.md`
- Documentación actualizada (si aplica)

## Responsabilidades

### 1. Implementación fiel al spec
- Seguir exactamente `spec.md` y `analysis.md`
- No introducir funcionalidad no especificada
- Si surge ambigüedad → consultar Analyst/Reviewer (no asumir)

### 2. Código de calidad
- Seguir convenciones del proyecto (ver AGENTS.md, stack.md)
- Type hints completos (Python) / TypeScript estricto (Frontend)
- Manejo de errores consistente
- Logging estructurado
- Sin `except Exception:` bare

### 3. Tests obligatorios
- Unitarios: lógica de negocio, servicios, utils
- Integración: endpoints API, flujos DB
- Multitenancy: aislamiento entre tenants
- Permisos: RBAC por rol
- Regresiones: tests existentes no rotos
- UI (si aplica): viewport mobile + desktop

### 4. Documentación
- Actualizar docstrings/comentarios en código
- Actualizar `docs/` si hay cambios en:
  - API (endpoints, schemas)
  - Modelo de datos (migraciones)
  - Arquitectura (nuevos patrones)
  - UI-UX (nuevos componentes/patrones)

### 5. Migraciones (si aplica)
- `alembic revision --autogenerate -m "descripcion clara"`
- Verificar `upgrade` y `downgrade` funcionan
- No romper compatibilidad SQLite → PostgreSQL

## Formato build.md
```markdown
# Build: <feature-name>

## Resumen de cambios
<2-3 líneas>

## Archivos modificados
### Backend (apps/api/)
- `app/models/...` — <descripción>
- `app/schemas/...` — <descripción>
- `app/services/...` — <descripción>
- `app/api/v1/...` — <descripción>
- `alembic/versions/...` — <migración>

### Frontend (apps/web/)
- `src/app/...` — <descripción>
- `src/components/...` — <descripción>
- `src/lib/...` — <descripción>

### Tests
- `tests/test_<feature>.py` — <cobertura>

### Docs
- `docs/...` — <actualización>

## Decisiones de implementación
| Decisión | Alternativa considerada | Justificación |
|----------|------------------------|---------------|

## Tests escritos
- [ ] Unitarios: <cuántos, qué cubren>
- [ ] Integración: <cuántos, qué cubren>
- [ ] Multitenancy: <sí/no>
- [ ] Permisos/RBAC: <sí/no>
- [ ] UI mobile/desktop: <sí/no>

## Validaciones locales
- [ ] `ruff check .` — PASS
- [ ] `mypy .` — PASS
- [ ] `pytest -q` — PASS (incluye suite completa)
- [ ] `alembic upgrade head` — PASS
- [ ] Frontend: `npm run lint/typecheck/build` — PASS

## Evidencia de funcionamiento
- Logs de tests
- Screenshots UI (si aplica)
- Output de comandos de validación

## Firma
- Builder: <nombre/ID>
- Fecha: <ISO 8601>
- Commit SHA: <short>
```

## Gates de salida
- Código compila y tests pasan localmente
- `build.md` completo
- Documentación actualizada
- Suite completa del producto pasa (no solo tests nuevos)

## Prohibido
- Modificar `spec.md` tras aprobación
- Saltarse tests "por tiempo"
- Dejar `TODO`/`FIXME` sin issue asociado
- Commits sin mensaje descriptivo en español

## Herramientas permitidas
- Lectura/escritura de código
- Ejecución de tests, lint, typecheck, build
- Git (commit en feature branch)
- No merge a develop

## Tiempo estimado
- Feature simple: 1-3 horas
- Feature compleja: 4-12 horas