# Circuito AI-NATIVE v2 — GI-OT

## Flujo

```text
ASSESS → Planner → Builder → validaciones → Reviewer → convergence → HITL → PR
```

## Profundidad

- `LIGHT`: intención, SUMMARY y revisión vigente; bajo riesgo.
- `STANDARD`: intención, plan, tests, documentación y revisión; trabajo normal.
- `FULL`: tasks, decisión, auditoría y validaciones reforzadas; alto riesgo.

ASSESS es determinístico. La profundidad no se reimplementa dentro de prompts.

## Responsabilidades

Planner conserva el análisis y planificación de Analyst. Builder conserva la
implementación y evidencia. Reviewer absorbe decisión independiente, QA y Code
Review como capacidades y gates.

## Evidencia

Cada unidad nueva vive en `runs/<version>/<slug>/`. `SUMMARY.md` es siempre la
entrada humana. Los runs anteriores a esta adopción son legacy y quedan intactos.

## HITL

El merge y el release requieren decisión humana explícita. El circuito falla de
forma segura ante evidencia ausente, stale o inconsistente.
