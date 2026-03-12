from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict
from typing import Any, Dict, List

from gaia_core.models import EnvironmentalObservation
from gaia_iot.planetary.publisher import PlanetaryStateSnapshot

logger = logging.getLogger(__name__)


class EdgeUplink:
    """
    Batched uplink from GAIA-IoT edge node to GAIA-Server.

    Features:
      - local ring buffer for offline tolerance
      - configurable batch size
      - exponential retry with max_retry limit
      - backpressure: stop enqueueing if buffer exceeds max_events
      - planetary-state snapshot queue (separate from observation buffer)
      - stub transport (replace with real gRPC AtlasObservationService.Ingest)

    Production transport:
      gRPC AtlasObservationService.Ingest + planetary_state_push() over mTLS/PQC
      Causal envelope required for Class A observations.
    """

    def __init__(self, substrate, config) -> None:
        self.substrate = substrate
        self.config = config
        self._buffer: deque[Dict[str, Any]] = deque(
            maxlen=config.buffer_max_events
        )
        self._snapshot_queue: deque[PlanetaryStateSnapshot] = deque(maxlen=64)
        self._running = False
        self._thread: threading.Thread | None = None
        self._sent = 0
        self._failed = 0
        self._snapshots_sent = 0
        self._lock = threading.Lock()

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()
        logger.info("EdgeUplink started. endpoint=%s batch=%d",
                    self.config.uplink_endpoint, self.config.uplink_batch_size)

    def stop(self) -> None:
        self._running = False
        logger.info("EdgeUplink stopped. sent=%d failed=%d snapshots_sent=%d",
                    self._sent, self._failed, self._snapshots_sent)

    def enqueue(self, observations: List[EnvironmentalObservation]) -> None:
        """Add observations to the uplink buffer."""
        with self._lock:
            for obs in observations:
                self._buffer.append({
                    "source_id":             obs.source_id,
                    "domain":                obs.domain,
                    "observed_at":           obs.observed_at.isoformat(),
                    "ingest_at":             obs.ingest_at.isoformat(),
                    "payload":               obs.payload,
                    "source_class":          obs.source_class.value,
                    "quality_score":         obs.quality_score,
                    "latency_seconds":       obs.latency_seconds,
                    "freshness_class":       obs.freshness_class,
                    "adversarial_suspicion": obs.adversarial_suspicion,
                })

    def enqueue_snapshot(self, snapshot: PlanetaryStateSnapshot) -> None:
        """Queue a planetary-state snapshot for uplink to GAIA-Server."""
        with self._lock:
            self._snapshot_queue.append(snapshot)
        logger.debug("EdgeUplink: snapshot queued. id=%s", snapshot.snapshot_id)

    def snapshot_queue_depth(self) -> int:
        with self._lock:
            return len(self._snapshot_queue)

    def buffer_depth(self) -> int:
        with self._lock:
            return len(self._buffer)

    def _flush_loop(self) -> None:
        while self._running:
            time.sleep(self.config.buffer_flush_interval_seconds)
            self._flush_batch()
            self._flush_snapshots()

    def _flush_snapshots(self) -> None:
        with self._lock:
            if not self._snapshot_queue:
                return
            snapshot = self._snapshot_queue.popleft()

        try:
            self._transmit_snapshot(snapshot)
            with self._lock:
                self._snapshots_sent += 1
            logger.info("EdgeUplink.flush_snapshot: id=%s obs=%d",
                        snapshot.snapshot_id, snapshot.observation_count)
        except Exception as exc:
            logger.warning("EdgeUplink.flush_snapshot failed: %s", exc)
            with self._lock:
                self._snapshot_queue.appendleft(snapshot)  # re-queue

    def _flush_batch(self) -> None:
        with self._lock:
            if not self._buffer:
                return
            batch = []
            for _ in range(min(self.config.uplink_batch_size, len(self._buffer))):
                batch.append(self._buffer.popleft())

        if not batch:
            return

        for attempt in range(1, self.config.uplink_retry_max + 1):
            try:
                self._transmit(batch)
                with self._lock:
                    self._sent += len(batch)
                logger.info("EdgeUplink.flush: sent=%d buffer_remaining=%d",
                            len(batch), self.buffer_depth())
                return
            except Exception as exc:
                logger.warning(
                    "EdgeUplink.flush attempt %d/%d failed: %s",
                    attempt, self.config.uplink_retry_max, exc,
                )
                if attempt < self.config.uplink_retry_max:
                    time.sleep(
                        self.config.uplink_retry_backoff_seconds * (2 ** (attempt - 1))
                    )

        logger.error(
            "EdgeUplink: all retries exhausted. Re-queuing %d observations.",
            len(batch),
        )
        with self._lock:
            self._failed += len(batch)
            for item in reversed(batch):
                self._buffer.appendleft(item)

    def _transmit(self, batch: List[Dict[str, Any]]) -> None:
        """
        Stub transmit. Replace with:
          channel = grpc.secure_channel(self.config.uplink_endpoint, credentials)
          stub = AtlasObservationServiceStub(channel)
          stub.Ingest(IngestRequest(observations=batch))
        """
        if not self.config.uplink_enabled:
            return
        for item in batch:
            self.substrate.dispatch("ATLAS", {
                "kind":    "uplink_batch_item",
                "payload": item,
            })

    def _transmit_snapshot(self, snapshot: PlanetaryStateSnapshot) -> None:
        """
        Stub planetary-state transmit. Replace with:
          stub.planetary_state_push(PlanetaryStatePushRequest(snapshot=snapshot))
        """
        if not getattr(self.config, "planetary_publish_enabled", True):
            return
        self.substrate.dispatch("NEXUS", {
            "kind":     "planetary_state_snapshot",
            "node_id":  snapshot.node_id,
            "snapshot": asdict(snapshot),
        })
