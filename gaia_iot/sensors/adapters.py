from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from gaia_core.models import ObservationSourceClass


class BaseAdapter:
    """
    Base sensor adapter stub.

    Production adapters replace read() with real hardware/API calls:
      - MODBUS/RS-485 for field stations
      - MQTT for low-cost IoT devices
      - REST/gRPC for regulatory feeds
      - satellite/remote-sensing APIs for S4 sources

    Adversarial suspicion is computed from:
      - anomaly scores vs historical baselines
      - source class credibility
      - cross-sensor consistency checks
    """

    SOURCE_CLASS: ObservationSourceClass = ObservationSourceClass.FIELD
    DOMAIN: str = "UNKNOWN"

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._open = False

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def read(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _base_reading(self, source_suffix: str, payload: Dict[str, Any],
                      latency_seconds: float = 120.0,
                      quality_score: float = 0.85,
                      adversarial_suspicion: float = 0.0) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        return {
            "source_id":             f"{self.node_id}-{self.DOMAIN.lower()}-{source_suffix}",
            "domain":                self.DOMAIN,
            "observed_at":           (now - timedelta(seconds=latency_seconds)).isoformat(),
            "ingest_at":             now.isoformat(),
            "payload":               payload,
            "source_class":          self.SOURCE_CLASS,
            "quality_score":         quality_score,
            "latency_seconds":       latency_seconds,
            "adversarial_suspicion": adversarial_suspicion,
        }


class TerraAdapter(BaseAdapter):
    """Terrestrial sensor adapter: soil, temperature, wildfire risk, seismic."""
    SOURCE_CLASS = ObservationSourceClass.FIELD
    DOMAIN = "TERRA"

    def read(self) -> Dict[str, Any]:
        return self._base_reading(
            source_suffix="01",
            payload={
                "temperature_c":    round(20.0 + random.gauss(0, 3), 2),
                "soil_moisture":    round(max(0.0, min(1.0, 0.25 + random.gauss(0, 0.05))), 3),
                "wildfire_risk":    round(max(0.0, min(1.0, 0.3 + random.gauss(0, 0.1))), 3),
                "seismic_activity": round(max(0.0, random.expovariate(10)), 4),
            },
            latency_seconds=random.uniform(60, 240),
            quality_score=round(random.uniform(0.75, 0.97), 3),
        )


class AquaAdapter(BaseAdapter):
    """Hydrological sensor adapter: river level, turbidity, dissolved oxygen."""
    SOURCE_CLASS = ObservationSourceClass.FIELD
    DOMAIN = "AQUA"

    def read(self) -> Dict[str, Any]:
        return self._base_reading(
            source_suffix="01",
            payload={
                "river_level_m":      round(1.2 + random.gauss(0, 0.15), 3),
                "turbidity_ntu":      round(max(0, 5.0 + random.gauss(0, 2)), 2),
                "dissolved_oxygen":   round(max(0, 8.5 + random.gauss(0, 0.5)), 3),
                "ph":                 round(max(0, min(14, 7.2 + random.gauss(0, 0.2))), 2),
                "conductivity_us_cm": round(max(0, 350 + random.gauss(0, 20)), 1),
            },
            latency_seconds=random.uniform(90, 360),
            quality_score=round(random.uniform(0.70, 0.95), 3),
        )


class AeroAdapter(BaseAdapter):
    """Atmospheric sensor adapter: air quality, weather, climate signals."""
    SOURCE_CLASS = ObservationSourceClass.LOW_COST_IOT
    DOMAIN = "AERO"

    def read(self) -> Dict[str, Any]:
        return self._base_reading(
            source_suffix="01",
            payload={
                "pm25_ug_m3":       round(max(0, 12.0 + random.gauss(0, 4)), 2),
                "pm10_ug_m3":       round(max(0, 22.0 + random.gauss(0, 6)), 2),
                "co2_ppm":          round(max(350, 415 + random.gauss(0, 10)), 1),
                "temperature_c":    round(18.0 + random.gauss(0, 4), 2),
                "humidity_pct":     round(max(0, min(100, 55 + random.gauss(0, 8))), 1),
                "pressure_hpa":     round(1013 + random.gauss(0, 5), 1),
                "wind_speed_mps":   round(max(0, 4.0 + random.gauss(0, 1.5)), 2),
            },
            latency_seconds=random.uniform(30, 180),
            quality_score=round(random.uniform(0.60, 0.88), 3),
            adversarial_suspicion=round(random.uniform(0.0, 0.12), 3),
        )


class VitaAdapter(BaseAdapter):
    """Biosphere sensor adapter: species count, habitat quality, biodiversity index."""
    SOURCE_CLASS = ObservationSourceClass.FIELD
    DOMAIN = "VITA"

    def read(self) -> Dict[str, Any]:
        return self._base_reading(
            source_suffix="01",
            payload={
                "species_count":       random.randint(12, 80),
                "biodiversity_index":  round(max(0, min(1, 0.65 + random.gauss(0, 0.08))), 3),
                "habitat_quality":     round(max(0, min(1, 0.72 + random.gauss(0, 0.06))), 3),
                "invasive_species_flag": random.random() < 0.05,
                "canopy_cover_pct":    round(max(0, min(100, 60 + random.gauss(0, 10))), 1),
            },
            latency_seconds=random.uniform(300, 1800),  # field reports are slower
            quality_score=round(random.uniform(0.65, 0.90), 3),
            adversarial_suspicion=0.0,
        )
