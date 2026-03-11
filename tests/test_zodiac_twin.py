"""
GAIA-IoT — Universal Zodiac Gaia Twin Test Suite
"""
import pytest
import numpy as np
from zodiac_twin.zodiac_registry import ZodiacRegistry
from zodiac_twin.love_utility import LoveUtility, LoveInput, LoveDecision
from zodiac_twin.harmony_engine import HarmonyEngine
from zodiac_twin.gaia_twin import GaiaTwin, SessionConfig


def test_all_12_signs_in_registry():
    signs = ZodiacRegistry.all_signs()
    assert len(signs) == 12
    names = {s.name for s in signs}
    for expected in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                     "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]:
        assert expected in names


def test_cancer_pemf_freq():
    cancer = ZodiacRegistry.get("Cancer")
    assert cancer.pemf_freq_hz == 42.8
    assert cancer.love_freq_hz == 528.0


def test_libra_love_freq():
    libra = ZodiacRegistry.get("Libra")
    assert libra.pemf_freq_hz == 528.0  # Libra IS the love throne


def test_harmony_engine_synthesizes_waveform():
    engine = HarmonyEngine(sample_rate_hz=1000, duration_sec=5)
    cancer = ZodiacRegistry.get("Cancer")
    wave = engine.synthesize(cancer)
    assert wave.waveform is not None
    assert len(wave.waveform) == 5000
    assert wave.peak_freq_hz > 0
    assert np.max(np.abs(wave.waveform)) <= 1.01  # Safety cap (1mT)


def test_love_utility_allow():
    util = LoveUtility()
    inputs = LoveInput(
        hrv_score=0.9, harmony_score=0.9, shadow_power=0.1, angel_power=0.9,
        pemf_coherence=0.85, sign_love_freq=528.0, schumann_alignment=0.9
    )
    result = util.evaluate(inputs)
    assert result.decision == LoveDecision.ALLOW
    assert result.love_score > 0.7


def test_love_utility_quarantine():
    util = LoveUtility()
    inputs = LoveInput(
        hrv_score=0.1, harmony_score=0.1, shadow_power=0.95, angel_power=0.05,
        pemf_coherence=0.1, sign_love_freq=42.8, schumann_alignment=0.1
    )
    result = util.evaluate(inputs)
    assert result.decision == LoveDecision.QUARANTINE


def test_gaia_twin_safety_exclusion():
    twin = GaiaTwin()
    config = SessionConfig(sign_name="Cancer", duration_sec=60)
    result = twin.run_session(config, exclusions=["pacemaker"])
    assert result.love_decision == LoveDecision.QUARANTINE
    assert "safety" in result.notes.lower()


def test_gaia_twin_sim_session():
    twin = GaiaTwin()
    config = SessionConfig(sign_name="Leo", duration_sec=10, hardware_output=False)
    result = twin.run_session(config)
    assert result.sign == "Leo"
    assert result.peak_freq_hz > 0


def test_full_zodiac_synthesize():
    engine = HarmonyEngine(sample_rate_hz=500, duration_sec=2)
    waves = engine.synthesize_full_zodiac()
    assert len(waves) == 12
    for wave in waves:
        assert np.max(np.abs(wave.waveform)) <= 1.01
