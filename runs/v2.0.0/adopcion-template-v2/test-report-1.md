# Test report 1 — adopcion-template-v2

## Gobernanza

- `py -m pytest -q tests`: **8 passed**.
- PowerShell parser sobre `scripts/*.ps1`: **PASS**.
- `check-integrity.ps1`: **PASS**.
- `mcp-tools.ps1`: **PASS (0 servers)**.
- `sync-agentic-adapters.ps1 -Check`: **PASS**.
- ASSESS: **PASS**, profundidad `STANDARD`.
- Materialización SDD: **PASS**.
- Convergence: **CONVERGED**, cero findings abiertos.

## Producto

- `py -m pytest -q apps/api/tests`: **106 passed**, 68 warnings deprecación.
- No se ejecutaron migraciones.
- Frontend build: **PASS** (`next build`, TypeScript y generación estática).
- Frontend lint: **FAIL**, por 17 errores y 26 warnings preexistentes en código
  de producto; no se modificaron fuentes para ocultarlos ni corregirlos dentro
  del alcance de esta feature de gobernanza.

## Alcance protegido

`git diff` no muestra cambios en `apps/api/app/**`, migraciones, `apps/web/src/**`,
`apps/web/public/**`, `apps/web/package*.json` ni en los runs legacy.
