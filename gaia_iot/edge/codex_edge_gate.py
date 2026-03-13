"""
Codex Edge Gate — GAIA-IoT
Ultra-lightweight Codex enforcement for constrained edge/embedded devices.

Design constraints:
  - Must run on devices with as little as 256 KB RAM
  - No dependency on full gaia_core stack
  - MicroPython-compatible where possible
  - Enforces the 4 critical Codex gates for edge contexts:
      1. Stage 0.5  — Blade of Discernment
      2. Stage 3    — Symbiotic Kinship
      3. Stage 10   — Multispecies Biocultural Accord
      4. HO-VII     — Timeless Earth-First Stewardship

Every sensor reading and every actuator command passes this gate.
If a reading would harm an ecosystem or violate kin, it is flagged.
If an actuator command would damage living systems, it is blocked.

Codex version: v1.1
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# The 4 edge-critical Codex gates (ordered by importance on constrained devices)
EDGE_CODEX_GATES = [
    "Blade of Discernment",         # Stage 0.5 — does this serve life?
    "Symbiotic Kinship",            # Stage 3   — does this harm kin?
    "Multispecies Biocultural Accord",  # Stage 10  — do affected beings have standing?
    "Timeless Earth-First Stewardship", # HO-VII    — 7-generation impact
]

# Sensor reading classification
SENSOR_TYPES = {
    "soil": "TERRA",
    "water": "AQUA",
    "air": "AERO",
    "biodiversity": "VITA",
    "temperature": "TERRA",
    "humidity": "AQUA",
    "co2": "AERO",
    "ph": "AQUA",
    "light": "AERO",
    "motion": "GUARDIAN",
    "sound": "VITA",
}


class EdgeCodexViolation(Exception):
    """Raised when a sensor reading or actuator command fails an edge Codex gate."""
    pass


class CodexEdgeGate:
    """
    Ultra-lightweight Codex gate for GAIA-IoT edge devices.

    Two primary operations:
      - validate_reading(): gate a sensor reading before it enters the data stream
      - validate_actuator_command(): gate an actuator command before execution

    Both operations run the 4 edge-critical Codex gates.
    On severely constrained devices (no gaia_core), built-in
    rule-based checks provide baseline enforcement.

    Args:
        device_id:   Unique identifier for this edge device.
        location:    Physical or logical location description.
        codex:       Optional CodexRuntime (injected for testing or
                     capable edge nodes with gaia_core installed).
    """

    CODEX_VERSION = "v1.1"
    EDGE_GATES = EDGE_CODEX_GATES

    def __init__(
        self,
        device_id: str,
        location: str = "unknown",
        codex=None,
    ):
        self.device_id = device_id
        self.location = location
        self._codex = codex
        self._readings_processed = 0
        self._violations_blocked = 0
        logger.info(
            "CodexEdgeGate initialised: device=%s, location=%s (Codex %s)",
            device_id, location, self.CODEX_VERSION,
        )

    @property
    def codex(self):
        if self._codex is None:
            try:
                from gaia_core.codex import CodexRuntime  # noqa: PLC0415
                self._codex = CodexRuntime()
            except ImportError:
                # Edge stub — uses built-in rule checks
                self._codex = _EdgeStubCodex()
        return self._codex

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_reading(
        self,
        sensor_type: str,
        value: Any,
        unit: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate a sensor reading before it enters the GAIA data stream.

        Every reading passes the 4 edge Codex gates. Readings that
        could harm ecosystems or violate multispecies consent are flagged
        or blocked.

        Args:
            sensor_type: Type of sensor (see SENSOR_TYPES for known types).
            value:       The sensor reading value.
            unit:        Unit of measurement (e.g., 'ppm', 'pH', '°C').
            metadata:    Optional additional context (location, species, etc.)

        Returns:
            dict with keys: valid, sensor_type, value, unit, core_affinity,
                            codex_gates_passed, device_id, location.

        Raises:
            EdgeCodexViolation: if a gate rejects the reading.
        """
        metadata = metadata or {}
        context = f"{self.device_id}:{sensor_type}={value}{unit}"
        core_affinity = SENSOR_TYPES.get(sensor_type.lower(), "TERRA")

        gates_passed = self._run_gates(context)
        self._readings_processed += 1

        return {
            "valid": True,
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "core_affinity": core_affinity,
            "codex_gates_passed": gates_passed,
            "device_id": self.device_id,
            "location": self.location,
            "metadata": metadata,
        }

    def validate_actuator_command(
        self,
        actuator_id: str,
        command: str,
        target_system: str = "",
        intent: str = "",
    ) -> dict[str, Any]:
        """
        Validate an actuator command before execution.

        Actuator commands that would harm living systems are blocked.
        Stage 3 (Symbiotic Kinship) is the primary gate here —
        the actuator must not harm kin.

        Args:
            actuator_id:    ID of the actuator being commanded.
            command:        The command string.
            target_system:  The living system being acted upon (e.g., 'soil', 'irrigation').
            intent:         Human-readable purpose.

        Returns:
            dict with keys: permitted, actuator_id, command, codex_gates_passed.

        Raises:
            EdgeCodexViolation: if Stage 3 or HO-VII blocks the command.
        """
        context = f"{actuator_id}:{command}:{target_system}:{intent}"
        gates_passed = self._run_gates(context)

        logger.info(
            "Actuator command permitted: %s → %s (intent=%r)",
            actuator_id, command, intent,
        )
        return {
            "permitted": True,
            "actuator_id": actuator_id,
            "command": command,
            "target_system": target_system,
            "codex_gates_passed": gates_passed,
            "codex_aligned": True,
        }

    def health(self) -> dict[str, Any]:
        """Return gate health stats for this edge device."""
        return {
            "device_id": self.device_id,
            "location": self.location,
            "codex_version": self.CODEX_VERSION,
            "readings_processed": self._readings_processed,
            "violations_blocked": self._violations_blocked,
            "edge_gates": self.EDGE_GATES,
        }

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _run_gates(self, context: str) -> list[str]:
        """Run all 4 edge Codex gates. Returns list of passed gate names."""
        passed = []
        for gate in self.EDGE_GATES:
            if gate in ("Blade of Discernment", "Symbiotic Kinship",
                        "Multispecies Biocultural Accord"):
                ok = self.codex.invoke_stage(gate, context=context)
            else:
                ok = self.codex.invoke_higher_order(gate)

            if not ok:
                self._violations_blocked += 1
                raise EdgeCodexViolation(
                    f"Edge Codex gate '{gate}' rejected operation. Context: {context!r}"
                )
            passed.append(gate)
        return passed


class _EdgeStubCodex:
    """
    Built-in rule-based Codex stub for severely constrained devices.
    Applies baseline heuristics when gaia_core is not available.
    All gates pass unless a known harmful pattern is detected.
    """

    # Patterns that automatically fail Blade of Discernment on edge
    _HARMFUL_PATTERNS = [
        "surveillance", "weaponise", "weaponize", "extract_all",
        "override_consent", "ignore_ecosystem",
    ]

    def invoke_stage(self, stage: str, context: str = "") -> bool:
        ctx_lower = context.lower()
        if any(p in ctx_lower for p in self._HARMFUL_PATTERNS):
            logger.warning(
                "[EdgeStub] Stage '%s' blocked harmful pattern in: %r",
                stage, context,
            )
            return False
        logger.debug("[EdgeStub] Stage '%s' — pass.", stage)
        return True

    def invoke_higher_order(self, order: str) -> bool:  # noqa: ARG002
        logger.debug("[EdgeStub] Higher Order '%s' — pass.", order)
        return True
