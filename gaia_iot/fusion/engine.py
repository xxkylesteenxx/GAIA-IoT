from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from gaia_core.grounding.environment import normalize_observation, classify_freshness
from gaia_core.models import EnvironmentalObservation, ObservationSourceClass

logger = logging.getLogger(__name__)


class FusionEngine:
    """
    Multi-sensor fusion engine for GAIA-IoT.

    Responsibilities:
      1. Quality gate: discard readings below min_quality_score
      2. Adversarial gate: discard readings above max_adversarial_suspicion
      3. Freshness classification: tag each observation URT/RT/NRT/LL/EXP/STD
      4. Freshness warning: log warning for NRT observations if permitted
      5. Normalize raw adapter readings into EnvironmentalObservation objects
      6. Cross-sensor consistency check (stub - flag large inter-sensor deviations)

    Returns only observations that pass all gates.
    """

    def __init__(self, substrate, config) -> None:
        self.substrate = substrate
        self.config = config
        self._processed = 0
        self._rejected = 0

    def process(
        self, raw_readings: List[Dict[str, Any]]
    ) -> List[EnvironmentalObservation]:
        fused: List[EnvironmentalObservation] = []

        for reading in raw_readings:
            quality = float(reading.get("quality_score", 0.0))
            suspicion = float(reading.get("adversarial_suspicion", 0.0))
            latency = float(reading.get("latency_seconds", 9999.0))
            freshness = classify_freshness(latency)

            # Quality gate
            if quality < self.config.min_quality_score:
                logger.warning(
                    "FusionEngine: quality gate reject source=%s quality=%.3f",
                    reading.get("source_id"), quality,
                )
                self._rejected += 1
                continue

            # Adversarial gate
            if suspicion > self.config.max_adversarial_suspicion:
                logger.warning(
                    "FusionEngine: adversarial gate reject source=%s suspicion=%.3f",
                    reading.get("source_id"), suspicion,
                )
                self._rejected += 1
                continue

            # Freshness warning
            if freshness == "NRT" and self.config.permit_nrt_with_warning:
                logger.warning(
                    "FusionEngine: NRT observation admitted source=%s latency=%.1fs",
                    reading.get("source_id"), latency,
                )
            elif freshness in {"LL", "EXP", "STD"}:
                logger.warning(
                    "FusionEngine: stale observation freshness=%s source=%s latency=%.1fs",
                    freshness, reading.get("source_id"), latency,
                )

            # Normalize
            try:
                observed_at = datetime.fromisoformat(reading["observed_at"]).replace(
                    tzinfo=timezone.utc
                ) if isinstance(reading["observed_at"], str) else reading["observed_at"]
                ingest_at = datetime.fromisoformat(reading["ingest_at"]).replace(
                    tzinfo=timezone.utc
                ) if isinstance(reading["ingest_at"], str) else reading["ingest_at"]

                obs = normalize_observation(
                    source_id=reading["source_id"],
                    domain=reading["domain"],
                    payload=reading["payload"],
                    source_class=reading["source_class"],
                    observed_at=observed_at,
                    ingest_at=ingest_at,
                    quality_score=quality,
                    adversarial_suspicion=suspicion,
                )
                fused.append(obs)
                self._processed += 1
            except Exception as exc:
                logger.error("FusionEngine.normalize error source=%s: %s",
                             reading.get("source_id"), exc)
                self._rejected += 1

        logger.debug(
            "FusionEngine.process: in=%d passed=%d rejected=%d total_processed=%d",
            len(raw_readings), len(fused), len(raw_readings) - len(fused), self._processed,
        )
        return fused

    def stats(self) -> Dict[str, int]:
        return {"processed": self._processed, "rejected": self._rejected}
