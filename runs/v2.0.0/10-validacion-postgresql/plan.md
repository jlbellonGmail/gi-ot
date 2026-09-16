# Plan — 10-validacion-postgresql

1. Ejecutar ASSESS FULL y materializar SDD.
2. Inventariar cada cambio de PR #2 con commit, decisión y destino.
3. Revisar migraciones sin modificar las históricas.
4. Incorporar PostgreSQL, RLS, constraints y fixtures mínimos.
5. Validar SQLite, PostgreSQL, seguridad y calidad.
6. Integrar sólo el gate PostgreSQL necesario al CI v2.
7. Ejecutar Reviewer, convergence y auditoría.
8. Publicar una nueva PR hacia develop sin merge automático.
