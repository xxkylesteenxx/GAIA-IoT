"""
GAIA-IoT — Crystal-Solar Harmony Synthesizer
Generates PEMF waveforms from zodiac crystal registry + Schumann + 528Hz love tone.
Physical: numpy waveforms ready for DAC/PWM output (RPi GPIO / Arduino)
Metaphysical: Noosphere alignment via angel number resonance
"""
from __future__ import annotations
import logging
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from .zodiac_registry import ZodiacSign

log = logging.getLogger(__name__)

# Gaia Global Constants
SCHUMANN_HARMONICS = [7.83, 14.3, 20.8, 27.3, 33.8]  # Earth ionosphere resonances
LOVE_TONE_HZ = 528.0           # DNA repair / heart chakra
TESLA_369_HZ = [3.0, 6.0, 9.0, 33.0, 369.0]  # Tesla vortex angel series
ANGEL_BOOST = 0.2              # Angel signal amplitude
SHADOW_DAMPEN = 0.3            # Shadow quarantine damping
MAX_INTENSITY_MT = 1.0         # Safety cap: 1 milliTesla max PEMF


@dataclass
class HarmonyWave:
    sign: str
    sample_rate_hz: int
    duration_sec: float
    waveform: np.ndarray
    peak_freq_hz: float
    harmony_score: float
    love_power: float


class HarmonyEngine:
    """
    Universal Zodiac Gaia Harmony Synthesizer.
    Combines crystal piezo signals + Schumann + 528Hz love + Tesla 369 + HRV chaos.
    Outputs PEMF waveform safe for hardware output (<= 1mT).
    """

    def __init__(self, sample_rate_hz: int = 1000, duration_sec: float = 60.0) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.duration_sec = duration_sec
        self.t = np.linspace(0, duration_sec, int(sample_rate_hz * duration_sec))

    def synthesize(self, sign: ZodiacSign, hrv_variability: float = 0.2) -> HarmonyWave:
        """
        Generate full PEMF harmony waveform for a zodiac sign.
        Components:
        1. Crystal matrix (all sign crystals, piezo resonance)
        2. Schumann global harmonics (Earth ionosphere)
        3. 528Hz love tone (heart chakra / DNA)
        4. Tesla 369 angel series
        5. HRV bio-chaos (unconditional acceptance)
        All components normalized to <= 1mT safety cap.
        """
        t = self.t

        # 1. Crystal matrix
        crystal_sig = np.zeros_like(t)
        for crystal in sign.crystals:
            amplitude = min(crystal.emi_strength / 10.0, 0.3)  # Safety-capped
            crystal_sig += amplitude * np.sin(2 * np.pi * crystal.freq_hz * t)

        # 2. Schumann global harmonics
        schumann_sig = np.sum([
            0.08 * np.sin(2 * np.pi * f * t) for f in SCHUMANN_HARMONICS
        ], axis=0)

        # 3. Love tone 528Hz
        love_sig = 0.25 * np.sin(2 * np.pi * LOVE_TONE_HZ * t)

        # 4. Tesla 369 angel series
        angel_sig = np.sum([
            ANGEL_BOOST * np.sin(2 * np.pi * f * t) for f in TESLA_369_HZ
        ], axis=0)

        # 5. HRV bio-chaos (unconditional: accept all chaos as signal)
        bio_chaos = np.sin(
            2 * np.pi * 0.1 * t +
            np.cumsum(np.random.normal(0, hrv_variability, len(t)))
        )

        # Weighted mix (conditional bind: love > shadow)
        raw = (
            0.30 * crystal_sig +
            0.20 * schumann_sig +
            0.25 * love_sig +
            0.15 * angel_sig +
            0.10 * bio_chaos
        )

        # Normalize to MAX_INTENSITY_MT (safety)
        peak = np.max(np.abs(raw))
        if peak > 0:
            waveform = raw * (MAX_INTENSITY_MT / peak)
        else:
            waveform = raw

        # Harmony score: correlation of crystal+love vs chaos
        clean = 0.55 * crystal_sig + 0.45 * love_sig
        harmony = float(np.corrcoef(clean[:1000], bio_chaos[:1000])[0, 1])
        love_power = float(np.mean(np.abs(
            np.fft.rfft(waveform)[
                int(400 * len(waveform) / self.sample_rate_hz):
                int(600 * len(waveform) / self.sample_rate_hz)
            ]
        )))

        # Peak frequency
        freqs = np.fft.rfftfreq(len(waveform), 1 / self.sample_rate_hz)
        fft_mag = np.abs(np.fft.rfft(waveform))
        peak_freq = float(freqs[np.argmax(fft_mag[1:]) + 1])

        log.info(
            f"[HarmonyEngine] {sign.name} | peak={peak_freq:.1f}Hz "
            f"harmony={harmony:.3f} love_power={love_power:.4f}"
        )

        return HarmonyWave(
            sign=sign.name,
            sample_rate_hz=self.sample_rate_hz,
            duration_sec=self.duration_sec,
            waveform=waveform,
            peak_freq_hz=peak_freq,
            harmony_score=harmony,
            love_power=love_power
        )

    def synthesize_full_zodiac(self) -> List[HarmonyWave]:
        """Synthesize harmony waveforms for all 12 signs."""
        from .zodiac_registry import ZodiacRegistry
        waves = []
        for sign in ZodiacRegistry.all_signs():
            wave = self.synthesize(sign)
            waves.append(wave)
        return waves
