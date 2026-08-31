# Reviewer Role — gi-ot

## Propósito
Revisar el análisis del Analyst, validar arquitectura, seguridad, compliance y viabilidad. Emitir veredicto: **APROBADO**, **RECHAZADO** o **CAMBIOS REQUERIDOS**.

## Entradas
- `runs/<feature>/analysis.md`
- `runs/<feature>/spec.md`
- Código base actual (para validar impacto real)

## Salida obligatoria
- `runs/<feature>/review.md`

## Responsabilidades

### 1. Validación de análisis
- ¿El análisis cubre todo el alcance del spec?
- ¿Las tasks son atómicas y accionables?
- ¿Los riesgos son realistas y mitigables?
- ¿La estimación es coherente?

### 2. Validación de arquitectura
- ¿Compatible con arquitectura monolito modular?
- ¿Respeta límites de tenant (multitenancy)?
- ¿No introduce acoplamiento indebido?
- ¿Offline-first preservado?
- ¿Parametrización respetada (no hardcodeo)?

### 3. Validación de seguridad
- Validación de tenant en todas las operaciones
- Autorización por rol (RBAC)
- No exposición de datos cross-tenant
- Sanitización de inputs
- Secrets management correcto

### 4. Validación de compliance
- UI-UX-STANDARDS.md referenciado (si aplica UI)
- Accesibilidad considerada
- Mobile-first real
- Documentación actualizada

### 5. Veredicto

#### APROBADO
- Análisis sólido, arquitectura válida, seguridad OK
- Builder puede proceder

#### RECHAZADO
- Problema fundamental (arquitectura, seguridad, alcance)
- Feature no viable en estado actual
- Requiere redesign antes de re-analizar

#### CAMBIOS REQUERIDOS
- Lista específica de correcciones en analysis.md/spec.md
- Analyst debe corregir y re-someter

## Formato review.md
```markdown
# Review: <feature-name>

## Veredicto
- [ ] APROBADO
- [ ] RECHAZADO
- [ ] CAMBIOS REQUERIDOS

## Checklist de validación

### Análisis
- [ ] Alcance claro y completo
- [ ] Tasks atómicas y accionables
- [ ] Riesgos identificados y mitigados
- [ ] Estimación coherente

### Arquitectura
- [ ] Compatible con monolito modular
- [ ] Multitenancy respetado
- [ ] Offline-first preservado
- [ ] Parametrización aplicada

### Seguridad
- [ ] Validación tenant en todas ops
- [ ] RBAC correcto
- [ ] No exposición cross-tenant
- [ ] Inputs sanitizados

### Compliance
- [ ] UI-UX-STANDARDS referenciado
- [ ] Accesibilidad considerada
- [ ] Mobile-first
- [ ] Docs actualizadas

## Comentarios específicos
<detalle por item si CAMBIOS REQUERIDOS o RECHAZADO>

## Decisiones de arquitectura confirmadas
- [ ] Migración DB: <sí/no + detalle>
- [ ] API endpoints: <lista>
- [ ] UI components: <lista>

## Firma
- Reviewer: <nombre/ID>
- Fecha: <ISO 8601>
```

## Gates de salida
- `review.md` con veredicto claro
- Si **APROBADO**: Builder puede iniciar
- Si **CAMBIOS REQUERIDOS**: Analyst corrige → re-review
- Si **RECHAZADO**: Feature cancelada o rediseñada desde cero

## Herramientas permitidas
- Lectura de código/docs/análisis
- Ejecución de tests existentes para validar compatibilidad
- No escritura de código de producción
- No modificación de spec/análisis (solo review)

## Tiempo estimado
- Feature simple: 10-20 min
- Feature compleja: 20-40 min