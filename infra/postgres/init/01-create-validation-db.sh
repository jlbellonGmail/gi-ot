#!/bin/sh
set -eu

: "${GIOT_DB_NAME:?GIOT_DB_NAME requerido}"
: "${GIOT_DB_USER:?GIOT_DB_USER requerido}"
: "${GIOT_DB_PASSWORD:?GIOT_DB_PASSWORD requerido}"

psql --set ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname postgres \
  --set app_db="$GIOT_DB_NAME" \
  --set app_user="$GIOT_DB_USER" \
  --set app_password="$GIOT_DB_PASSWORD" <<'EOSQL'
SELECT format(
  'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS',
  :'app_user',
  :'app_password'
) \gexec
SELECT format('CREATE DATABASE %I OWNER %I', :'app_db', :'app_user') \gexec
EOSQL
