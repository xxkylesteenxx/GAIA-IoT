from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from gaia_iot.sensors.adapters import (
    TerraAdapter, AquaAdapter, AeroAdapter, VitaAdapter
)

logger = logging.getLogger(__name__)


class SensorManager:
    """
    Manages all sensor adapters for the IoT node.

    Enabled domains (per config.enabled_domains) map to adapters:
      TERRA -> TerraAdapter  (land, soil, wildfire, seismic)
      AQUA  -> AquaAdapter   (rivers, watersheds, oceans)
      AERO  -> AeroAdapter   (air quality, weather, climate)
      VITA  -> VitaAdapter   (species, habitats, biodiversity)

    collect() returns a list of raw adapter readings ready for
    fusion quality-gating.
    """

    ADAPTER_MAP = {
        "TERRA": TerraAdapter,
        "AQUA":  AquaAdapter,
        "AERO":  AeroAdapter,
        "VITA":  VitaAdapter,
    }

    def __init__(self, config) -> None:
        self.config = config
        self._adapters = {}
        self._running = False
        self._lock = threading.Lock()

        for domain in config.enabled_domains:
            cls = self.ADAPTER_MAP.get(domain)
            if cls:
                self._adapters[domain] = cls(node_id=config.node_id)
                logger.info("SensorAdapter registered: domain=%s", domain)
            else:
                logger.warning("Unknown sensor domain: %s", domain)

    def start(self) -> None:
        self._running = True
        for adapter in self._adapters.values():
            adapter.open()

    def stop(self) -> None:
        self._running = False
        for adapter in self._adapters.values():
            adapter.close()

    def collect(self) -> List[Dict[str, Any]]:
        """Poll all adapters and return raw reading dicts."""
        readings: List[Dict[str, Any]] = []
        for domain, adapter in self._adapters.items():
            try:
                reading = adapter.read()
                readings.append(reading)
                logger.debug("SensorManager.collect domain=%s source=%s",
                             domain, reading.get("source_id"))
            except Exception as exc:
                logger.error("SensorManager.collect error domain=%s: %s", domain, exc)
        return readings

    def adapter_count(self) -> int:
        return len(self._adapters)
