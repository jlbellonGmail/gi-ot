# Stack tecnológico — gi-ot

## Propósito

Este documento define únicamente el stack tecnológico aprobado para `gi-ot`.

El detalle de arquitectura irá en `docs/tecnica/arquitectura.md`.

El detalle de persistencia irá en `docs/tecnica/modelo-datos.md`.

---

## Estrategia

Evolución prevista:

`BOOTSTRAP local → MVP → PostgreSQL → Producción SaaS`

Durante BOOTSTRAP se priorizan:

* simplicidad;
* ejecución local;
* bajo costo;
* mínima infraestructura.

---

## Frontend

* Next.js 16.x
* React
* TypeScript
* PWA
* diseño mobile-first y responsive

Ubicación:

`apps/web/`

Una única aplicación servirá a todos los tenants.

No desarrollar inicialmente apps Android/iOS nativas.

---

## Offline

Tecnologías:

* Service Worker
* Cache Storage
* IndexedDB

Objetivos:

* instalación en celular;
* trabajo sin conexión;
* almacenamiento local;
* operaciones pendientes;
* sincronización posterior;
* cámara;
* fotografías;
* QR.

---

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy 2.x
* Alembic

Ubicación:

`apps/api/`

Arquitectura inicial:

**monolito modular**

API inicial:

**REST versionada**

Ejemplo:

`/api/v1/...`

---

## Persistencia local — BOOTSTRAP

* SQLite
* SQLAlchemy
* Alembic

Objetivo:

ejecutar `gi-ot` localmente sin PostgreSQL, Supabase ni servicios externos.

SQLite no será la base de producción.

---

## Persistencia — Producción

* PostgreSQL
* SQLAlchemy
* psycopg
* Alembic

Modelo multitenant inicial:

`shared database + shared schema + tenant_id`

PostgreSQL utilizará Row-Level Security cuando corresponda para reforzar el aislamiento.

---

## Compatibilidad SQLite → PostgreSQL

Desde el inicio:

* evitar SQL específico de SQLite;
* usar SQLAlchemy;
* usar Alembic;
* mantener tipos compatibles;
* diseñar pensando en PostgreSQL;
* incorporar `tenant_id`;
* preferir UUID para entidades principales.

El paso SQLite → PostgreSQL no debe requerir reescribir el dominio.

---

## Multitenancy

`gi-ot` será multitenant desde la primera versión funcional.

Todos los tenants compartirán:

* aplicación;
* API;
* esquema lógico.

El aislamiento se implementará mediante:

* identidad autenticada;
* tenant activo;
* autorización;
* filtrado obligatorio por tenant;
* pruebas multitenant;
* RLS en PostgreSQL.

No crear aplicaciones ni backends independientes por empresa.

---

## Autenticación y autorización

Autenticación gestionada inicialmente por el backend.

No depender de Supabase Auth.

Modelo de autorización:

**RBAC**

Roles iniciales:

* `PLATFORM_OWNER`
* `TENANT_ADMIN`
* `TENANT_OFFICE`
* `TENANT_TECHNICIAN`

Los permisos se validarán siempre en backend.

---

## Fotografías y archivos

BOOTSTRAP:

`data/uploads/`

Producción:

**Object Storage S3-compatible**

La base almacenará metadatos y referencias, no los archivos binarios principales.

---

## Desarrollo local

Stack mínimo:

```text
Next.js
+
FastAPI
+
SQLite
+
filesystem local
```

No son obligatorios inicialmente:

* PostgreSQL local;
* Supabase;
* Docker;
* Redis;
* brokers;
* servicios cloud.

---

## Producción

Stack objetivo:

```text
Next.js / PWA
      ↓
FastAPI
      ↓
PostgreSQL
      +
Object Storage
```

Frontend:

* Vercel inicialmente.

Backend:

* contenedor independiente.

Base:

* PostgreSQL administrado.

Archivos:

* Object Storage S3-compatible.

Los proveedores concretos de backend, PostgreSQL y storage se decidirán más adelante.

---

## Validación antes de producción

Secuencia:

`SQLite → MVP local → PostgreSQL de validación → tests multitenant → RLS → producción`

Las funciones críticas deberán probarse contra PostgreSQL antes del despliegue.

---

## Tests

Backend:

* pytest

Priorizar:

* reglas de negocio;
* autenticación;
* autorización;
* multitenancy;
* sincronización;
* regresiones.

Las herramientas frontend se definirán cuando sean necesarias.

---

## No incorporar durante BOOTSTRAP

Salvo necesidad demostrada:

* microservicios;
* Kubernetes;
* Redis;
* RabbitMQ;
* Kafka;
* Elasticsearch;
* GraphQL;
* CQRS;
* event sourcing;
* Supabase;
* aplicación móvil nativa.

---

## Stack consolidado

### BOOTSTRAP

* Next.js + React + TypeScript + PWA
* FastAPI
* SQLite
* SQLAlchemy
* Alembic
* IndexedDB
* almacenamiento local

### PRODUCCIÓN

* Next.js / PWA
* FastAPI
* PostgreSQL
* SQLAlchemy
* psycopg
* Alembic
* `tenant_id`
* RLS
* Object Storage S3-compatible
* Vercel para frontend
* contenedor independiente para backend

---

## Regla final

No incorporar una nueva tecnología si el stack actual resuelve correctamente el problema.

Toda modificación relevante del stack requiere una decisión explícita y actualización de este documento.
