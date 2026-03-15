"""Integration: IoT node consumes Core dual-plane storage via bootstrap.

IoT nodes are resource-constrained edge devices. These tests verify the
full storage contract is honoured even at the edge: objects/, semantic/,
and views/ are all created and operational.
"""
from __future__ import annotations
import pytest
from gaia_core.bootstrap import build_default_gaia
from gaia_core.storage.schemas import PlaneLayout, StorageCapability
from gaia_core.storage.object_id import ObjectKind
from gaia_core.storage.semantic_index import SemanticRecord


@pytest.fixture
def substrate(tmp_path):
    return build_default_gaia(root=tmp_path / ".gaia_state")


def test_iot_substrate_has_storage(substrate):
    assert substrate.has_storage is True


def test_iot_sensor_event_write(substrate):
    """IoT nodes primarily write sensor-event objects."""
    oid = substrate.object_store.put(
        b'{"sensor": "temp", "value": 23.4}',
        kind=ObjectKind.EVENT,
    )
    assert substrate.object_store.get(oid) is not None


def test_iot_semantic_index_queryable(substrate):
    rec = SemanticRecord(
        object_id="iot-rec-001",
        kind=ObjectKind.EVENT.value,
        tags=["sensor", "temperature"],
        trust_level="verified",
    )
    substrate.object_store.index.put(rec)
    results = substrate.object_store.index.filter(tags=["sensor"])
    assert any(r.object_id == "iot-rec-001" for r in results)


def test_iot_sensor_view_exists(substrate):
    ids = [v.view_id for v in substrate.view_registry.list_views()]
    assert "by-kind-sensor" in ids


def test_iot_storage_capabilities(substrate):
    caps = substrate.storage_capabilities()
    assert StorageCapability.CONTENT_ADDRESSED in caps
    assert StorageCapability.SEMANTIC_INDEX in caps


def test_iot_plane_dirs_exist(substrate, tmp_path):
    layout = PlaneLayout(tmp_path / ".gaia_state")
    for plane in (layout.objects, layout.semantic, layout.views):
        assert plane.is_dir(), f"Missing: {plane}"


def test_iot_snapshot_storage_block(substrate):
    snap = substrate.consciousness_snapshot()
    assert "storage" in snap
