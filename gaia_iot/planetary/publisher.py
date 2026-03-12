"""PlanetaryStatePublisher: converts fused IoT observations into
partial PlanetaryState snapshots and hands them to EdgeUplink.

A PlanetaryState snapshot from an IoT node is intentionally partial:
only the domains observed by *this* node are populated. GAIA-Server
aggregates partial snapshots from the fleet into a unified view.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, List, Sequence

from gaia_iot.config import IoTConfig

logger = logging.getLogger(__name__)


@dataclass
class PlanetaryStateSnapshot:
    """Partial planetary-state contribution from one IoT node."""
    schema_version: str = "1.0"
    node_id: str = ""
    snapshot_id: str = ""
    captured_at: float = field(default_factory=time.time)  # unix epoch

    # Domain partials — only populated for domains this node observes.
    # Each entry is a free-form dict so connectors can add arbitrary fields
    # without breaking the envelope contract.
    terra: dict[str, Any] = field(default_factory=dict)   # soil / land
    aqua: dict[str, Any] = field(default_factory=dict)    # water
    aero: dict[str, Any] = field(default_factory=dict)    # atmosphere
    vita: dict[str, Any] = field(default_factory=dict)    # biosphere / life

    # Fleet metadata
    observation_count: int = 0
    quality_floor: float = 0.0   # min quality_score across contributing obs
    quality_ceiling: float = 1.0 # max quality_score across contributing obs

    # Causal linkage
    causal_cursor: str | None = None  # JetStream sequence pointer
    metadata: dict[str, Any] = field(default_factory=dict)


class PlanetaryStatePublisher:
    """
    Converts a batch of fused EnvironmentalObservations into a
    PlanetaryStateSnapshot and exposes it for uplink.

    Usage:
        publisher = PlanetaryStatePublisher(config)
        snapshot  = publisher.build_snapshot(fused_observations)
        uplink.enqueue_snapshot(snapshot)
    """

    def __init__(self, config: IoTConfig) -> None:
        self._config = config
        self._seq = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_snapshot(self, observations: Sequence[Any]) -> PlanetaryStateSnapshot:
        """Build a PlanetaryStateSnapshot from a fused observation batch."""
        self._seq += 1
        snapshot = PlanetaryStateSnapshot(
            node_id=self._config.node_id,
            snapshot_id=f"{self._config.node_id}:snap:{self._seq}",
        )

        if not observations:
            return snapshot

        quality_scores: list[float] = []

        for obs in observations:
            domain = getattr(obs, "domain", "").upper()
            payload = getattr(obs, "payload", {}) or {}
            quality = getattr(obs, "quality_score", 0.0)
            quality_scores.append(quality)
            source_id = getattr(obs, "source_id", "")

            entry = {"source_id": source_id, "quality": quality, **payload}

            if domain == "TERRA":
                snapshot.terra[source_id] = entry
            elif domain == "AQUA":
                snapshot.aqua[source_id] = entry
            elif domain == "AERO":
                snapshot.aero[source_id] = entry
            elif domain in ("VITA", "BIO"):
                snapshot.vita[source_id] = entry
            else:
                # unknown domain — stash in metadata for audit
                snapshot.metadata.setdefault("unknown_domains", {})
                snapshot.metadata["unknown_domains"][source_id] = {
                    "domain": domain, **entry
                }

        snapshot.observation_count = len(observations)
        if quality_scores:
            snapshot.quality_floor = min(quality_scores)
            snapshot.quality_ceiling = max(quality_scores)

        logger.debug(
            "PlanetaryStatePublisher: snapshot=%s obs=%d domains=terra:%d aqua:%d aero:%d vita:%d",
            snapshot.snapshot_id,
            snapshot.observation_count,
            len(snapshot.terra),
            len(snapshot.aqua),
            len(snapshot.aero),
            len(snapshot.vita),
        )
        return snapshot
