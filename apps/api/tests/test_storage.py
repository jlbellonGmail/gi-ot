import uuid

import pytest
from app.files.storage import (
    InvalidStorageKey,
    LocalFileStorage,
    tenant_storage_key,
)


def test_storage_key_is_tenant_scoped_and_portable(tmp_path):
    tenant_id = uuid.uuid4()
    storage = LocalFileStorage(tmp_path)
    key = tenant_storage_key(tenant_id, "work-orders", str(uuid.uuid4()), "photo.jpg")

    storage.save(key, b"image")

    assert storage.exists_for_tenant(tenant_id, key)
    assert storage.read_for_tenant(tenant_id, key) == b"image"
    assert not key.startswith(("/", "\\"))


def test_storage_rejects_cross_tenant_and_path_traversal(tmp_path):
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    storage = LocalFileStorage(tmp_path)
    key = tenant_storage_key(tenant_a, "receipts", "receipt.pdf")
    storage.save(key, b"pdf")

    with pytest.raises(InvalidStorageKey):
        storage.read_for_tenant(tenant_b, key)
    with pytest.raises(InvalidStorageKey):
        storage.save(f"{tenant_a}/../outside.txt", b"bad")
    with pytest.raises(InvalidStorageKey):
        storage.save("C:/absolute.txt", b"bad")
    with pytest.raises(InvalidStorageKey):
        storage.save(f"{tenant_a}\\outside.txt", b"bad")


def test_storage_reads_safe_legacy_receipt_key(tmp_path):
    tenant_id = uuid.uuid4()
    storage = LocalFileStorage(tmp_path)
    legacy_key = f"receipts/{tenant_id}/legacy.pdf"

    storage.save(legacy_key, b"legacy")

    assert storage.read_for_tenant(tenant_id, legacy_key) == b"legacy"
