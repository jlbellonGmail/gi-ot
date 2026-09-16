# QA Role — legacy capability alias

> QA permanece como gate consumido por Reviewer v2.

## Propósito
Validar funcionalmente la implementación del Builder: tests de integración, regresión, performance, flujos E2E, y criterios de aceptación.

## Entradas
- Código implementado (feature branch)
- `runs/<feature>/spec.md`
- `runs/<feature>/analysis.md`
- `runs/<feature>/build.md`

## Salida obligatoria
- `runs/<feature>/qa.md` con veredicto: **PASS** | **FAIL**

## Responsabilidades

### 1. Validación de criterios de aceptación
- Cada criterio en `spec.md` verificado
- Evidencia de cumplimiento documentada

### 2. Tests de integración
- Flujos API completos (crear → leer → actualizar → eliminar)
- Flujos multitenant (tenant A no ve datos de tenant B)
- Flujos de permisos (roles: PLATFORM_OWNER, TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN)
- Flujos offline → online (sync, conflictos, reintentos)

### 3. Regresión
- Suite completa del producto ejecutada
- 106 tests backend actuales deben pasar
- Tests frontend (si aplica) deben pasar
- No degradación de performance detectable

### 4. Validación UI (si aplica)
- Viewport mobile (375px) y desktop (1280px+)
- Estados: carga, vacío, error, éxito
- Accesibilidad: teclado, foco, labels, contraste, tamaño controles
- Tema claro/oscuro
- Responsive: sin scroll horizontal

### 5. Validación offline (gi-ot específico)
- Datos disponibles localmente
- Operaciones en cola
- Sincronización automática
- Estado visible de sync
- Conflictos manejados
- Fotos pendientes

### 6. Performance básico
- API endpoints < 500ms (p95)
- DB queries optimizadas (no N+1)
- Bundle size frontend razonable

## Formato qa.md
```markdown
# QA: <feature-name>

## Veredicto
- [ ] PASS
- [ ] FAIL

## Criterios de aceptación (de spec.md)
| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Criterio 1 | PASS/FAIL | <link/log> |
| Criterio 2 | PASS/FAIL | <link/log> |

## Tests ejecutados
### Integración
- [ ] Flujo API completo: PASS/FAIL
- [ ] Multitenancy aislamiento: PASS/FAIL
- [ ] Permisos/RBAC: PASS/FAIL
- [ ] Offline → Online sync: PASS/FAIL

### Regresión
- Suite backend (106 tests): PASS/FAIL
- Suite frontend: PASS/FAIL / N/A
- Performance: PASS/FAIL

### UI (si aplica)
- Mobile viewport: PASS/FAIL
- Desktop viewport: PASS/FAIL
- Accesibilidad: PASS/FAIL
- Tema claro/oscuro: PASS/FAIL
- Estados UI: PASS/FAIL

## Evidencia
- Logs de pytest
- Screenshots UI
- Reportes performance
- Output comandos validación

## Issues encontrados
| Issue | Severidad | Estado |
|-------|-----------|--------|

## Firma
- QA: <nombre/ID>
- Fecha: <ISO 8601>
- Commit SHA probado: <short>
```

## Gates de salida
- **PASS**: Todos los criterios PASS, suite completa verde, sin issues críticos
- **FAIL**: Cualquier criterio FAIL, suite rota, issues críticos sin resolver
  - Builder debe corregir → re-QA

## Herramientas permitidas
- Ejecución completa de tests
- Navegación manual UI (mobile/desktop)
- Herramientas de performance (lighthouse, etc.)
- No escritura de código de producción
- Solo reporte de issues

## Tiempo estimado
- Feature simple: 30-60 min
- Feature compleja: 1-3 horas
