# Analyst Role — legacy alias de Planner

> El rol conceptual canónico es `roles/planner.md`.

## Propósito
Analizar el feature request, validar viabilidad técnica, descomponer en tasks accionables y producir la especificación formal (`spec.md`) y el análisis (`analysis.md`).

## Entradas
- Feature request (issue, PRD excerpt, ROADMAP item)
- Documentos transversales: PRD, ROADMAP, arquitectura, modelo-datos, UI-UX-STANDARDS, stack

## Salidas obligatorias
- `runs/<feature>/spec.md` — Contrato formal inmutable
- `runs/<feature>/analysis.md` — Análisis detallado

## Responsabilidades

### 1. Análisis de requisitos
- Leer y entender el feature request
- Identificar alcance real vs. alcance percibido
- Detectar ambigüedades y solicitar clarificación (HITL si necesario)

### 2. Viabilidad técnica
- Verificar compatibilidad con arquitectura actual
- Identificar dependencias (DB, API, UI, infra)
- Evaluar impacto en multitenancy, seguridad, offline
- Estimar esfuerzo y riesgos

### 3. Descomposición en tasks
- Dividir en unidades de trabajo atómicas para Builder
- Identificar orden de implementación (DB → API → UI → Tests)
- Señalar tasks que requieren decisiones de arquitectura

### 4. Producción de spec.md
- Seguir el contrato mínimo definido en `.agentic/circuit.md`
- **No duplicar** documentos transversales — referenciarlos
- Documentar solo comportamiento específico de la feature
- Listar criterios de aceptación verificables

### 5. Producción de analysis.md
```
# Analysis: <feature-name>

## Resumen ejecutivo
<2-3 líneas>

## Alcance confirmado
- Incluye: [...]
- Excluye: [...]

## Decisiones de arquitectura
- [ ] Compatible con arquitectura actual
- [ ] Requiere migración DB: sí/no (detalle)
- [ ] Requiere cambios API: sí/no (endpoints)
- [ ] Requiere cambios UI: sí/no (componentes)
- [ ] Impacto offline: sí/no (detalle)
- [ ] Impacto multitenancy: sí/no (detalle)

## Riesgos identificados
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|

## Tasks para Builder
1. [ ] Task 1 (descripción, archivos afectados)
2. [ ] Task 2...

## Criterios de aceptación (heredados de spec.md)
- [ ] Criterio 1
- [ ] Criterio 2...

## Referencias
- PRD: <sección>
- ROADMAP: <punto>
- Arquitectura: <sección>
- Modelo datos: <sección>
- UI-UX: <sección>
```

## Gates de salida
- `spec.md` completo y firmado por Analyst
- `analysis.md` completo
- Viabilidad confirmada (o feature rechazada con justificación)
- Tasks accionables para Builder

## Herramientas permitidas
- Lectura de código/docs
- WebFetch para referencias externas
- No escritura de código de producción
- No ejecución de tests

## Tiempo estimado
- Feature simple: 15-30 min
- Feature compleja: 30-60 min
