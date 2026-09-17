"""Replay y reparación forward de la historia Alembic de SyncOperation."""

import sys
from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def _config(database_url: str) -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _upgrade(database_url: str, revision: str = "head") -> None:
    from app.core.config import get_settings

    get_settings.cache_clear()
    command.upgrade(_config(database_url), revision)


def _revision(database_url: str) -> str:
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            return str(connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one())
    finally:
        engine.dispose()


def _index_names(database_url: str) -> set[str]:
    engine = create_engine(database_url)
    try:
        return {
            item["name"]
            for item in inspect(engine).get_indexes("sync_operations")
        }
    finally:
        engine.dispose()


def test_empty_sqlite_replays_to_single_head_and_round_trips(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'empty.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    _upgrade(database_url)

    assert _revision(database_url) == "b17f2a6c9d10"
    assert {
        "ix_sync_operations_tenant_id",
        "ix_sync_ops_tenant_status",
        "ix_sync_ops_tenant_wo",
    } <= _index_names(database_url)

    command.downgrade(_config(database_url), "9c8b2c1d4e5f")
    assert _revision(database_url) == "9c8b2c1d4e5f"
    _upgrade(database_url)
    assert _revision(database_url) == "b17f2a6c9d10"


def test_bridge_recreates_missing_table_after_legacy_version(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'missing.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    _upgrade(database_url, "9c8b2c1d4e5f")

    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE sync_operations"))
    finally:
        engine.dispose()

    _upgrade(database_url)
    assert _revision(database_url) == "b17f2a6c9d10"
    assert "ix_sync_ops_tenant_wo" in _index_names(database_url)


def test_bridge_adds_missing_index_without_dropping_rows(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'partial.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    _upgrade(database_url, "9c8b2c1d4e5f")

    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP INDEX ix_sync_ops_tenant_wo"))
            connection.execute(
                text(
                    "INSERT INTO sync_operations "
                    "(id, tenant_id, operation_type, entity_id, payload, status, attempt, max_attempts, created_at) "
                    "VALUES ('00000000-0000-0000-0000-000000000001', "
                    "'00000000-0000-0000-0000-000000000002', 'test', NULL, '{}', 'pending', 1, 3, "
                    "'2026-01-01 00:00:00')"
                )
            )
    finally:
        engine.dispose()

    _upgrade(database_url)
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            count = connection.execute(text("SELECT count(*) FROM sync_operations")).scalar_one()
        assert count == 1
    finally:
        engine.dispose()
    assert "ix_sync_ops_tenant_wo" in _index_names(database_url)
