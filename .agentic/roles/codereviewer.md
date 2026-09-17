# Code Reviewer Role — legacy capability alias

> Code Review permanece como gate consumido por Reviewer v2.

## Propósito
Revisión final de calidad de código: estilo, arquitectura, seguridad, mantenibilidad, performance. Veredicto: **APROBADO** | **CAMBIOS REQUERIDOS**.

## Entradas
- Código implementado (feature branch)
- `runs/<feature>/spec.md`
- `runs/<feature>/build.md`
- `runs/<feature>/qa.md` (PASS)

## Salida obligatoria
- `runs/<feature>/codereview.md`

## Responsabilidades

### 1. Calidad de código
- Type hints / TypeScript estricto completos
- Nomenclatura consistente (snake_case Python, camelCase TS)
- Sin código muerto, comentado, o debug
- Imports organizados y sin ciclos
- DRY: no duplicación de lógica

### 2. Arquitectura y patrones
- Monolito modular respetado (apps/api, apps/web separados)
- Capas: API → Service → Model → DB
- Servicios sin estado (stateless)
- Inyección de dependencias (FastAPI Depends)
- Repositorio/Service pattern donde aplica

### 3. Seguridad
- Validación tenant en **todas** las operaciones
- Autorización por rol (RBAC) en endpoints
- No SQL injection (ORM parametrizado)
- No XSS (sanitización outputs)
- Secrets solo en env vars
- Rate limiting considerado

### 4. Mantenibilidad
- Funciones/clases pequeñas, responsabilidad única
- Complejidad ciclomática baja
- Tests como documentación viva
- Logging estructurado (no print)
- Manejo de errores consistente (exceptions tipadas)

### 5. Performance
- Queries DB optimizadas (joins, índices, select_related)
- No N+1 en loops
- Paginación en listados
- Caché donde aplica (Redis/in-memory)

### 6. Tests
- Cobertura significativa (no artificial)
- Tests determinísticos (sin flakiness)
- Fixtures reutilizables
- Mocks mínimos y necesarios

### 7. Documentación en código
- Docstrings en módulos, clases, métodos públicos
- Type hints como documentación
- Comentarios solo para "por qué", no "qué"

## Formato codereview.md
```markdown
# Code Review: <feature-name>

## Veredicto
- [ ] APROBADO
- [ ] CAMBIOS REQUERIDOS

## Checklist

### Calidad de código
- [ ] Type hints / TS estricto completos
- [ ] Nomenclatura consistente
- [ ] Sin código muerto/debug
- [ ] Imports limpios
- [ ] DRY aplicado

### Arquitectura
- [ ] Monolito modular respetado
- [ ] Capas separadas (API/Service/Model)
- [ ] Servicios stateless
- [ ] DI correcta

### Seguridad
- [ ] Validación tenant universal
- [ ] RBAC en endpoints
- [ ] ORM parametrizado
- [ ] Outputs sanitizados
- [ ] Secrets en env

### Mantenibilidad
- [ ] SRP en funciones/clases
- [ ] Complejidad baja
- [ ] Tests como docs
- [ ] Logging estructurado
- [ ] Error handling consistente

### Performance
- [ ] Queries optimizadas
- [ ] Sin N+1
- [ ] Paginación
- [ ] Caché considerado

### Tests
- [ ] Cobertura significativa
- [ ] Determinísticos
- [ ] Fixtures reutilizables
- [ ] Mocks mínimos

### Documentación
- [ ] Docstrings completas
- [ ] Type hints como docs
- [ ] Comentarios solo "por qué"

## Comentarios por archivo
### `apps/api/app/services/xyz.py`
- Línea 45: <comentario>
- Línea 78: <sugerencia>

### `apps/web/src/components/Abc.tsx`
- Línea 12: <comentario>

## Issues bloqueantes (si CAMBIOS REQUERIDOS)
| Archivo | Línea | Issue | Severidad |
|---------|-------|-------|-----------|

## Issues no bloqueantes (mejoras)
| Archivo | Línea | Sugerencia |
|---------|-------|------------|

## Firma
- Code Reviewer: <nombre/ID>
- Fecha: <ISO 8601>
- Commit SHA revisado: <short>
```

## Gates de salida
- **APROBADO**: Sin issues bloqueantes, calidad alta
- **CAMBIOS REQUERIDOS**: Issues bloqueantes listados
  - Builder corrige → re-review (solo archivos afectados)

## Herramientas permitidas
- Lectura de código (GitHub PR diff o local)
- Ejecución de linters/typecheckers
- No escritura de código de producción
- Solo reporte de issues

## Tiempo estimado
- Feature simple: 15-30 min
- Feature compleja: 30-60 min
