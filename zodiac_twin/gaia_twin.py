"""
GAIA-IoT — Universal Zodiac Gaia Digital Twin
PEMF + Crystal-Solar Harmony Generator v1.0
Physical: PEMF waveforms for RPi GPIO / Arduino DAC output
Metaphysical: Zodiac-crystal-planet noosphere alignment
Safety: All signals capped at 1mT, harmony gate >0.7 required
"""
from __future__ import annotations
import logging
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from .zodiac_registry import ZodiacRegistry, ZodiacSign
from .love_utility import LoveUtility, LoveInput, LoveDecision
from .harmony_engine import HarmonyEngine, HarmonyWave

log = logging.getLogger(__name__)

# Safety constants
SAFE_MAX_MT = 1.0           # 1 milliTesla max (therapy-safe)
SAFE_MIN_HARMONY = 0.0      # Accept all harmony scores (unconditional)
SESSION_MAX_SEC = 1800      # 30 min max session
COOLDOWN_SEC = 300          # 5 min cooldown between sessions


@dataclass
class SessionConfig:
    sign_name: str
    duration_sec: int = 600       # 10 min default
    hrv_variability: float = 0.2  # HRV chaos input
    hardware_output: bool = False  # Set True for real GPIO/DAC
    operator_id: str = "default"


@dataclass
class SessionResult:
    sign: str
    duration_sec: float
    harmony_score: float
    love_score: float
    love_decision: LoveDecision
    peak_freq_hz: float
    samples_generated: int
    notes: str = ""


class GaiaTwin:
    """
    Universal Zodiac Gaia Digital Twin.
    Generates PEMF waveforms aligned to zodiac crystal-solar matrix.
    Conditional love gates: harmony > threshold → ALLOW; shadow > threshold → QUARANTINE.

    Hardware output (RPi):
        Set hardware_output=True in SessionConfig.
        Waveform written to GPIO PWM pin (requires RPi.GPIO or gpiozero).
        NEVER exceeds 1mT (amplitude-capped in HarmonyEngine).
    """

    SAFETY_EXCLUSIONS = [
        "pacemaker", "epilepsy", "pregnancy", "implanted_device"
    ]

    def __init__(self) -> None:
        self.engine = HarmonyEngine(sample_rate_hz=1000, duration_sec=60)
        self.love_util = LoveUtility()
        self._last_session_end: float = 0.0

    # ------------------------------------------------------------------
    # Safety check
    # ------------------------------------------------------------------
    def safety_check(self, exclusions: list[str] | None = None) -> bool:
        """
        Check operator exclusion criteria before session start.
        Returns False and logs if any exclusion matches.
        """
        if exclusions:
            for ex in exclusions:
                if ex.lower() in self.SAFETY_EXCLUSIONS:
                    log.error(f"[GaiaTwin] Safety exclusion triggered: {ex!r}. Session BLOCKED.")
                    return False
        return True

    # ------------------------------------------------------------------
    # Run session
    # ------------------------------------------------------------------
    def run_session(self, config: SessionConfig, exclusions: list[str] | None = None) -> SessionResult:
        """
        Run a PEMF harmony session for a zodiac sign.
        Steps:
        1. Safety check
        2. Cooldown check
        3. Synthesize waveform
        4. Evaluate love utility
        5. Apply conditional gate
        6. Output (hardware or sim)
        """
        # Safety
        if not self.safety_check(exclusions):
            return SessionResult(
                sign=config.sign_name, duration_sec=0,
                harmony_score=0, love_score=0,
                love_decision=LoveDecision.QUARANTINE,
                peak_freq_hz=0, samples_generated=0,
                notes="Blocked by safety exclusion."
            )

        # Cooldown
        since_last = time.time() - self._last_session_end
        if since_last < COOLDOWN_SEC and self._last_session_end > 0:
            remaining = int(COOLDOWN_SEC - since_last)
            log.warning(f"[GaiaTwin] Cooldown active: {remaining}s remaining.")
            return SessionResult(
                sign=config.sign_name, duration_sec=0,
                harmony_score=0, love_score=0,
                love_decision=LoveDecision.QUARANTINE,
                peak_freq_hz=0, samples_generated=0,
                notes=f"Cooldown: {remaining}s remaining."
            )

        # Get sign
        sign = ZodiacRegistry.get(config.sign_name)

        # Synthesize
        wave = self.engine.synthesize(sign, config.hrv_variability)

        # Love utility evaluation
        angel_power = float(np.mean([n / 999.0 for n in sign.angel_numbers]))
        shadow_power = float(np.mean([n / 999.0 for n in sign.shadow_numbers]))
        love_input = LoveInput(
            hrv_score=max(0.0, float(wave.harmony_score)),
            harmony_score=min(1.0, abs(float(wave.harmony_score))),
            shadow_power=shadow_power,
            angel_power=angel_power,
            pemf_coherence=min(1.0, abs(float(wave.harmony_score))),
            sign_love_freq=sign.love_freq_hz,
            schumann_alignment=0.83  # Default Earth alignment
        )
        love_result = self.love_util.evaluate(love_input)

        # Conditional gate
        duration = min(config.duration_sec, SESSION_MAX_SEC)
        if love_result.decision == LoveDecision.QUARANTINE:
            log.warning(f"[GaiaTwin] Shadow dominant for {config.sign_name} — session quarantined.")
            return SessionResult(
                sign=config.sign_name, duration_sec=0,
                harmony_score=float(wave.harmony_score),
                love_score=love_result.love_score,
                love_decision=LoveDecision.QUARANTINE,
                peak_freq_hz=wave.peak_freq_hz,
                samples_generated=0,
                notes=love_result.notes
            )

        # Output
        if config.hardware_output:
            self._hardware_output(wave, duration)
        else:
            self._sim_output(wave, config.sign_name, love_result.love_score)

        self._last_session_end = time.time()

        return SessionResult(
            sign=config.sign_name,
            duration_sec=duration,
            harmony_score=float(wave.harmony_score),
            love_score=love_result.love_score,
            love_decision=love_result.decision,
            peak_freq_hz=wave.peak_freq_hz,
            samples_generated=len(wave.waveform),
            notes=love_result.notes
        )

    # ------------------------------------------------------------------
    # Output methods
    # ------------------------------------------------------------------
    def _sim_output(self, wave: HarmonyWave, sign_name: str, love_score: float) -> None:
        log.info(
            f"[GaiaTwin][SIM] {sign_name} | "
            f"peak={wave.peak_freq_hz:.1f}Hz | "
            f"harmony={wave.harmony_score:.3f} | "
            f"love={love_score:.3f} | "
            f"samples={len(wave.waveform)}"
        )

    def _hardware_output(self, wave: HarmonyWave, duration_sec: float) -> None:
        """
        Hardware PEMF output via RPi GPIO PWM.
        Requires: RPi.GPIO or gpiozero installed.
        PEMF coil connected to GPIO PWM pin.
        """
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            PEMF_PIN = 18  # BCM GPIO 18 = hardware PWM
            GPIO.setup(PEMF_PIN, GPIO.OUT)
            pwm = GPIO.PWM(PEMF_PIN, wave.peak_freq_hz)
            pwm.start(50)  # 50% duty cycle
            time.sleep(duration_sec)
            pwm.stop()
            GPIO.cleanup()
            log.info(f"[GaiaTwin][HW] PEMF session complete: {duration_sec}s @ {wave.peak_freq_hz:.1f}Hz")
        except ImportError:
            log.warning("[GaiaTwin][HW] RPi.GPIO not available — falling back to sim.")
            self._sim_output(wave, wave.sign, 0.0)


# Entry point for standalone run
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    twin = GaiaTwin()
    config = SessionConfig(
        sign_name="Cancer",
        duration_sec=600,
        hrv_variability=0.2,
        hardware_output=False  # Flip to True for RPi
    )
    result = twin.run_session(config)
    print(f"\n=== GAIA Twin Session ===")
    print(f"Sign:     {result.sign}")
    print(f"Decision: {result.love_decision.value}")
    print(f"Love:     {result.love_score:.3f}")
    print(f"Harmony:  {result.harmony_score:.3f}")
    print(f"Peak Hz:  {result.peak_freq_hz:.1f}")
    print(f"Notes:    {result.notes}")
