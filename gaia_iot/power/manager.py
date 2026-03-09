from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class PowerManager:
    """
    Adaptive power manager for GAIA-IoT edge nodes.

    Power modes:
      full       - all sensors active, minimum poll interval
      balanced   - all sensors active, standard poll interval (default)
      low-power  - reduced sensor set, extended poll interval, lower uplink frequency
      sleep      - minimal activity, only critical sensors, maximum intervals

    Battery thresholds:
      < battery_threshold_low      -> downgrade to low-power
      < battery_threshold_critical -> downgrade to sleep

    Production integration:
      - read battery level from /sys/class/power_supply/BAT0/capacity
      - or from a hardware power monitor IC over I2C
    """

    MODE_POLL_MULTIPLIERS: Dict[str, float] = {
        "full":      0.5,
        "balanced":  1.0,
        "low-power": 3.0,
        "sleep":     10.0,
    }

    def __init__(self, config) -> None:
        self.config = config
        self._mode = config.power_mode

    def current_mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in self.MODE_POLL_MULTIPLIERS:
            raise ValueError(f"Unknown power mode: {mode}")
        if mode != self._mode:
            logger.info("PowerManager: mode change %s -> %s", self._mode, mode)
            self._mode = mode

    def update_from_battery(self, battery_fraction: float) -> None:
        """Automatically downgrade power mode based on battery level."""
        if battery_fraction < self.config.battery_threshold_critical:
            self.set_mode("sleep")
        elif battery_fraction < self.config.battery_threshold_low:
            self.set_mode("low-power")
        else:
            # Don't auto-upgrade; only operator can restore to full/balanced
            pass

    def poll_interval(self, base_seconds: float) -> float:
        """Return the effective poll interval for the current power mode."""
        return base_seconds * self.MODE_POLL_MULTIPLIERS.get(self._mode, 1.0)

    def is_sensor_active(self, domain: str) -> bool:
        """In sleep mode, only TERRA and AERO critical sensors remain active."""
        if self._mode == "sleep":
            return domain in {"TERRA", "AERO"}
        return True

    def snapshot(self) -> Dict[str, object]:
        return {
            "mode":             self._mode,
            "poll_multiplier":  self.MODE_POLL_MULTIPLIERS[self._mode],
        }
