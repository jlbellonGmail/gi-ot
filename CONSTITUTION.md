# Constitución de GI-OT

## Principios estables

1. GI-OT sigue siendo un SaaS multitenant, multirrubro, parametrizable,
   mobile-first y preparado para offline.
2. El dominio, sus contratos API y su modelo de datos son propiedad de GI-OT;
   el mecanismo agéntico no los sustituye.
3. La gobernanza debe ser proporcional al riesgo: LIGHT, STANDARD y FULL.
4. Las validaciones determinísticas prevalecen sobre instrucciones duplicadas
   en prompts.
5. Planner, Builder y Reviewer son capacidades independientes del proveedor,
   modelo o herramienta de ejecución.
6. Toda operación crítica conserva evidencia trazable al commit evaluado.
7. Un gate fallido bloquea el avance y conserva el diagnóstico.
8. No se destruye trabajo ajeno para resolver conflictos locales.
9. El merge y el release requieren decisión humana explícita.
10. La adopción brownfield preserva historia, contratos funcionales y rollback.
11. MCP y Skills se incorporan sólo ante una necesidad demostrable.
12. Ningún cambio de gobernanza puede crear dependencia funcional del futuro
    core/SaaS.

La aplicación operativa de estos principios vive en `AGENTS.md`, los contratos
ejecutables en `scripts/` y la evidencia primaria en `runs/`.
