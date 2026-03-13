"""
Multispecies Monitor — GAIA-IoT
Stage 10 (Multispecies Biocultural Accord) compliant environmental monitor.

Gives non-human stakeholders — soil microbiota, watersheds, pollinators,
species communities, atmospheric systems — **standing** in the GAIA
data stream. Their wellbeing is not a metric to be optimised; it is a
voice to be heard.

Every reading from a sensor in a living system is treated as a
message from that system. This monitor translates those messages
into a format the rest of GAIA can act on — with the same weight
as a human user’s request.

Codex version: v1.1  
Primary cores: TERRA, AQUA, AERO, VITA
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

logger = logging.getLogger(__name__)


class StakeholderType(str, Enum):
    SOIL        = "soil"        # TERRA core
    WATER       = "water"       # AQUA core
    ATMOSPHERE  = "atmosphere"  # AERO core
    BIODIVERSITY = "biodiversity" # VITA core
    WATERSHED   = "watershed"   # AQUA + TERRA
    SPECIES     = "species"     # VITA core
    MICROBIOME  = "microbiome"  # TERRA + VITA
    CLIMATE     = "climate"     # AERO + HO-VII


# Core affinity map — which consciousness core speaks for each stakeholder
CORE_AFFINITY: dict[StakeholderType, list[str]] = {
    StakeholderType.SOIL:         ["TERRA"],
    StakeholderType.WATER:        ["AQUA"],
    StakeholderType.ATMOSPHERE:   ["AERO"],
    StakeholderType.BIODIVERSITY: ["VITA"],
    StakeholderType.WATERSHED:    ["AQUA", "TERRA"],
    StakeholderType.SPECIES:      ["VITA"],
    StakeholderType.MICROBIOME:   ["TERRA", "VITA"],
    StakeholderType.CLIMATE:      ["AERO"],
}


@dataclass
class StakeholderReading:
    """
    A single environmental reading from a non-human stakeholder.

    Fields:
        stakeholder_type: What kind of living system sent this signal.
        sensor_id:        ID of the sensor that captured the reading.
        metric:           What was measured (e.g., 'soil_moisture', 'ph', 'species_count').
        value:            The measured value.
        unit:             Unit of measurement.
        location:         Where the reading was taken.
        wellbeing_signal: Qualitative interpretation ('thriving'|'stable'|'stressed'|'critical').
        cores_notified:   Which consciousness cores receive this reading.
        codex_gates_passed: Codex gates that validated this reading.
        raw_metadata:     Any additional context from the sensor.
    """
    stakeholder_type: StakeholderType
    sensor_id: str
    metric: str
    value: Any
    unit: str = ""
    location: str = "unknown"
    wellbeing_signal: str = "stable"  # 'thriving' | 'stable' | 'stressed' | 'critical'
    cores_notified: list[str] = field(default_factory=list)
    codex_gates_passed: list[str] = field(default_factory=list)
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class MultispeciesMonitor:
    """
    Stage 10 — Multispecies Biocultural Accord — compliant monitor.

    Ingests sensor readings from living systems, validates them
    through the Codex Edge Gate, interprets their wellbeing signal,
    notifies the appropriate consciousness cores, and feeds the
    Zodiac Twin digital representations.

    Non-human beings have equal standing here. A critical soil
    moisture reading has the same urgency as a human alert.

    Args:
        device_id:  ID of the edge device hosting this monitor.
        location:   Physical location of the monitoring station.
        edge_gate:  Optional CodexEdgeGate instance.
        codex:      Optional CodexRuntime.
    """

    CODEX_VERSION = "v1.1"

    def __init__(
        self,
        device_id: str,
        location: str = "unknown",
        edge_gate=None,
        codex=None,
    ):
        self.device_id = device_id
        self.location = location
        self._edge_gate = edge_gate
        self._codex = codex
        self._readings: list[StakeholderReading] = []
        self._alerts: list[StakeholderReading] = []
        logger.info(
            "MultispeciesMonitor initialised: device=%s, location=%s",
            device_id, location,
        )

    @property
    def edge_gate(self):
        if self._edge_gate is None:
            from gaia_iot.edge.codex_edge_gate import CodexEdgeGate  # noqa: PLC0415
            self._edge_gate = CodexEdgeGate(
                device_id=self.device_id,
                location=self.location,
                codex=self._codex,
            )
        return self._edge_gate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(
        self,
        stakeholder_type: StakeholderType,
        sensor_id: str,
        metric: str,
        value: Any,
        unit: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> StakeholderReading:
        """
        Ingest a reading from a non-human stakeholder.

        1. Validates through CodexEdgeGate
        2. Interprets wellbeing signal
        3. Notifies appropriate consciousness cores
        4. Feeds Zodiac Twin if available
        5. Raises alert if wellbeing is 'stressed' or 'critical'

        Args:
            stakeholder_type: Type of living system.
            sensor_id:        Sensor identifier.
            metric:           What was measured.
            value:            Measured value.
            unit:             Unit of measurement.
            metadata:         Optional context.

        Returns:
            StakeholderReading with full Codex metadata.
        """
        metadata = metadata or {}

        # Codex gate
        gate_result = self.edge_gate.validate_reading(
            sensor_type=stakeholder_type.value,
            value=value,
            unit=unit,
            metadata=metadata,
        )

        # Interpret wellbeing
        wellbeing = self._interpret_wellbeing(metric, value, stakeholder_type)

        # Determine which cores to notify
        cores = CORE_AFFINITY.get(stakeholder_type, ["TERRA"])

        reading = StakeholderReading(
            stakeholder_type=stakeholder_type,
            sensor_id=sensor_id,
            metric=metric,
            value=value,
            unit=unit,
            location=self.location,
            wellbeing_signal=wellbeing,
            cores_notified=cores,
            codex_gates_passed=gate_result.get("codex_gates_passed", []),
            raw_metadata=metadata,
        )

        self._readings.append(reading)

        # Alert if stressed or critical
        if wellbeing in ("stressed", "critical"):
            self._raise_alert(reading)

        # Zodiac Twin update
        self._feed_zodiac_twin(reading)

        # Celebration on thriving signal
        if wellbeing == "thriving":
            logger.info(
                "🌍 [Celebration] %s at %s is THRIVING: %s=%s%s ❤️",
                stakeholder_type.value, self.location, metric, value, unit,
            )

        logger.info(
            "Reading ingested: %s | %s=%s%s | wellbeing=%s | cores=%s",
            stakeholder_type.value, metric, value, unit, wellbeing, cores,
        )
        return reading

    def get_alerts(self) -> list[StakeholderReading]:
        """Return all active stressed/critical alerts."""
        return list(self._alerts)

    def summary(self) -> dict[str, Any]:
        """Return a summary of all readings for this monitoring station."""
        wellbeing_counts: dict[str, int] = {}
        for r in self._readings:
            wellbeing_counts[r.wellbeing_signal] = wellbeing_counts.get(r.wellbeing_signal, 0) + 1
        return {
            "device_id": self.device_id,
            "location": self.location,
            "total_readings": len(self._readings),
            "active_alerts": len(self._alerts),
            "wellbeing_distribution": wellbeing_counts,
            "codex_version": self.CODEX_VERSION,
            "stage_10_compliant": True,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _interpret_wellbeing(
        metric: str,
        value: Any,
        stakeholder_type: StakeholderType,
    ) -> str:
        """
        Interpret a sensor value as a wellbeing signal.
        Built-in heuristics — override with domain-specific logic.
        """
        # Generic numeric thresholds — a starting point, not gospel
        try:
            v = float(value)
        except (TypeError, ValueError):
            return "stable"

        # Soil moisture (%) heuristics
        if metric in ("soil_moisture", "moisture") and stakeholder_type == StakeholderType.SOIL:
            if v >= 40:  return "thriving"
            if v >= 20:  return "stable"
            if v >= 10:  return "stressed"
            return "critical"

        # Water pH heuristics
        if metric == "ph" and stakeholder_type == StakeholderType.WATER:
            if 6.5 <= v <= 8.5:  return "thriving"
            if 6.0 <= v <= 9.0:  return "stable"
            if 5.5 <= v <= 9.5:  return "stressed"
            return "critical"

        # CO2 ppm heuristics (atmospheric)
        if metric in ("co2", "co2_ppm") and stakeholder_type == StakeholderType.ATMOSPHERE:
            if v <= 400:  return "thriving"
            if v <= 450:  return "stable"
            if v <= 500:  return "stressed"
            return "critical"

        # Species count heuristics (biodiversity)
        if metric == "species_count" and stakeholder_type == StakeholderType.BIODIVERSITY:
            if v >= 20:  return "thriving"
            if v >= 10:  return "stable"
            if v >= 5:   return "stressed"
            return "critical"

        return "stable"  # default for unknown metrics

    def _raise_alert(self, reading: StakeholderReading) -> None:
        """Record an alert and notify GUARDIAN + relevant cores."""
        self._alerts.append(reading)
        logger.warning(
            "⚠️  MULTISPECIES ALERT [%s]: %s=%s%s | wellbeing=%s | location=%s | cores=%s",
            reading.stakeholder_type.value,
            reading.metric, reading.value, reading.unit,
            reading.wellbeing_signal,
            reading.location,
            reading.cores_notified,
        )
        # Notify GUARDIAN
        try:
            from gaia_core.guardian import GUARDIAN  # noqa: PLC0415
            GUARDIAN.handle_multispecies_alert(reading)
        except ImportError:
            pass  # GUARDIAN not available on this edge node — log only

    def _feed_zodiac_twin(self, reading: StakeholderReading) -> None:
        """Feed the reading to the Zodiac Twin digital representation."""
        try:
            from zodiac_twin.twin import ZodiacTwin  # noqa: PLC0415
            ZodiacTwin.update(
                stakeholder=reading.stakeholder_type.value,
                metric=reading.metric,
                value=reading.value,
                wellbeing=reading.wellbeing_signal,
                location=reading.location,
            )
        except ImportError:
            pass  # Zodiac Twin not available on this node — graceful skip
