"""Backend local de archivos con claves portables y aisladas por tenant."""

from pathlib import Path, PurePosixPath
from typing import Protocol
from uuid import UUID


class InvalidStorageKey(ValueError):
    """La clave no es relativa, segura o no pertenece al tenant esperado."""


class StorageBackend(Protocol):
    """Contrato mínimo sustituible por object storage sin tocar el dominio."""

    def save(self, key: str, content: bytes) -> None: ...

    def read_for_tenant(self, tenant_id: UUID, key: str) -> bytes: ...

    def delete_for_tenant(self, tenant_id: UUID, key: str) -> None: ...

    def exists_for_tenant(self, tenant_id: UUID, key: str) -> bool: ...


def tenant_storage_key(tenant_id: UUID, *parts: str) -> str:
    """Construye una clave nueva con el tenant como primer namespace."""

    return "/".join((str(tenant_id), *parts))


class LocalFileStorage:
    """Filesystem local que nunca expone paths absolutos como storage keys."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    @staticmethod
    def _parts(key: str) -> tuple[str, ...]:
        if not key or "\\" in key or "\x00" in key:
            raise InvalidStorageKey("Clave de almacenamiento inválida")
        raw_parts = key.split("/")
        if any(part in {"", ".", ".."} or ":" in part for part in raw_parts):
            raise InvalidStorageKey("Clave de almacenamiento inválida")
        path = PurePosixPath(key)
        if path.is_absolute():
            raise InvalidStorageKey("La clave debe ser relativa")
        return tuple(path.parts)

    @classmethod
    def _validate_tenant(cls, tenant_id: UUID, key: str) -> tuple[str, ...]:
        parts = cls._parts(key)
        tenant = str(tenant_id)
        is_current = parts[0] == tenant
        is_legacy_receipt = (
            len(parts) >= 3 and parts[0] == "receipts" and parts[1] == tenant
        )
        if not (is_current or is_legacy_receipt):
            raise InvalidStorageKey("La clave no pertenece al tenant")
        return parts

    def _path(self, parts: tuple[str, ...]) -> Path:
        candidate = self.root.joinpath(*parts).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise InvalidStorageKey("La clave escapa del storage configurado") from exc
        return candidate

    def save(self, key: str, content: bytes) -> None:
        parts = self._parts(key)
        target = self._path(parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def read_for_tenant(self, tenant_id: UUID, key: str) -> bytes:
        return self._path(self._validate_tenant(tenant_id, key)).read_bytes()

    def delete_for_tenant(self, tenant_id: UUID, key: str) -> None:
        self._path(self._validate_tenant(tenant_id, key)).unlink(missing_ok=True)

    def exists_for_tenant(self, tenant_id: UUID, key: str) -> bool:
        return self._path(self._validate_tenant(tenant_id, key)).is_file()

    def local_path_for_tenant(self, tenant_id: UUID, key: str) -> Path:
        """Compatibilidad acotada para verificaciones locales y tooling."""

        return self._path(self._validate_tenant(tenant_id, key))
