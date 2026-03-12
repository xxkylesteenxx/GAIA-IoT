"""Tests for PlanetaryStatePublisher."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pytest

from gaia_iot.config import IoTConfig
from gaia_iot.planetary.publisher import PlanetaryStatePublisher, PlanetaryStateSnapshot


# ---------------------------------------------------------------------------
# Minimal observation stub (no gaia_core.models import needed)
# ---------------------------------------------------------------------------

class _SourceClass(str, Enum):
    CLASS_A = "class_a"
    CLASS_B = "class_b"


@dataclass
class _Obs:
    source_id: str
    domain: str
    payload: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.9
    source_class: _SourceClass = _SourceClass.CLASS_A


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config() -> IoTConfig:
    return IoTConfig(node_id="test-node-01")


@pytest.fixture
def publisher(config: IoTConfig) -> PlanetaryStatePublisher:
    return PlanetaryStatePublisher(config)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_empty_observations_returns_snapshot(publisher):
    snap = publisher.build_snapshot([])
    assert isinstance(snap, PlanetaryStateSnapshot)
    assert snap.observation_count == 0


def test_snapshot_node_id(publisher, config):
    snap = publisher.build_snapshot([])
    assert snap.node_id == config.node_id


def test_snapshot_id_format(publisher, config):
    snap = publisher.build_snapshot([])
    assert snap.snapshot_id.startswith(config.node_id)
    assert ":snap:" in snap.snapshot_id


def test_snapshot_ids_increment(publisher):
    s1 = publisher.build_snapshot([])
    s2 = publisher.build_snapshot([])
    assert s1.snapshot_id != s2.snapshot_id


def test_terra_observation_routed(publisher):
    obs = [_Obs(source_id="soil-01", domain="TERRA", payload={"moisture": 0.42})]
    snap = publisher.build_snapshot(obs)
    assert "soil-01" in snap.terra
    assert snap.terra["soil-01"]["moisture"] == 0.42


def test_aqua_observation_routed(publisher):
    obs = [_Obs(source_id="river-01", domain="AQUA", payload={"ph": 7.1})]
    snap = publisher.build_snapshot(obs)
    assert "river-01" in snap.aqua


def test_aero_observation_routed(publisher):
    obs = [_Obs(source_id="air-01", domain="AERO", payload={"co2_ppm": 415})]
    snap = publisher.build_snapshot(obs)
    assert "air-01" in snap.aero


def test_vita_observation_routed(publisher):
    obs = [_Obs(source_id="bio-01", domain="VITA", payload={"species_count": 12})]
    snap = publisher.build_snapshot(obs)
    assert "bio-01" in snap.vita


def test_bio_domain_alias_routed_to_vita(publisher):
    obs = [_Obs(source_id="bio-02", domain="BIO")]
    snap = publisher.build_snapshot(obs)
    assert "bio-02" in snap.vita


def test_unknown_domain_goes_to_metadata(publisher):
    obs = [_Obs(source_id="x-01", domain="UNKNOWN_DOMAIN")]
    snap = publisher.build_snapshot(obs)
    assert "unknown_domains" in snap.metadata
    assert "x-01" in snap.metadata["unknown_domains"]


def test_observation_count(publisher):
    obs = [
        _Obs("s1", "TERRA"),
        _Obs("s2", "AQUA"),
        _Obs("s3", "AERO"),
    ]
    snap = publisher.build_snapshot(obs)
    assert snap.observation_count == 3


def test_quality_floor_and_ceiling(publisher):
    obs = [
        _Obs("s1", "TERRA", quality_score=0.5),
        _Obs("s2", "AQUA",  quality_score=0.9),
    ]
    snap = publisher.build_snapshot(obs)
    assert snap.quality_floor == pytest.approx(0.5)
    assert snap.quality_ceiling == pytest.approx(0.9)


def test_multi_domain_snapshot(publisher):
    obs = [
        _Obs("t1", "TERRA"),
        _Obs("a1", "AQUA"),
        _Obs("r1", "AERO"),
        _Obs("v1", "VITA"),
    ]
    snap = publisher.build_snapshot(obs)
    assert len(snap.terra) == 1
    assert len(snap.aqua) == 1
    assert len(snap.aero) == 1
    assert len(snap.vita) == 1
    assert snap.observation_count == 4
