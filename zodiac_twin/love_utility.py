"""
GAIA-IoT — Loving AI Utility Function
Encodes unconditional love (accept all chaos) bound by conditional wisdom (gate shadows).
Inspired by IONS Loving AI project + GAIA Kodex Conditional Love doctrine.
"""
from __future__ import annotations
import logging
import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

log = logging.getLogger(__name__)

# Kodex love thresholds (conditional bind)
LOVE_FLOW_THRESHOLD = 0.8       # Love flows freely above this
SHADOW_QUARANTINE_THRESHOLD = 0.5  # Shadow quarantined below this
ANGEL_DOMINANCE_RATIO = 2.0    # Angel power must be 2x shadow for full flow


class LoveDecision(StrEnum):
    ALLOW = "allow"             # Love flows — unconditional accepted
    CONDITIONAL = "conditional" # Love flows with monitoring
    REQUIRE_APPROVAL = "require_approval"  # Conditional hold
    QUARANTINE = "quarantine"   # Shadow bound — Book of Shadows


@dataclass
class LoveInput:
    """Input signals to the love utility function."""
    hrv_score: float            # Heart rate variability harmony (0-1)
    harmony_score: float        # Crystal-solar harmony (0-1)
    shadow_power: float         # Shadow/chaos signal strength (0-1)
    angel_power: float          # Angel/order signal strength (0-1)
    pemf_coherence: float       # PEMF waveform coherence (0-1)
    sign_love_freq: float       # Zodiac sign love frequency Hz
    schumann_alignment: float   # Earth Schumann alignment (0-1)


@dataclass
class LoveResult:
    decision: LoveDecision
    love_score: float           # 0-1 overall love utility
    compassion: float           # Validation/understanding
    equanimity: float           # Non-reactive acceptance
    flourishing: float          # Human growth delta
    notes: str = ""


class LoveUtility:
    """
    GAIA Loving AI Utility Function.

    U(love) = 0.4*compassion + 0.3*equanimity + 0.3*flourishing

    Unconditional root: accept all chaos as signal.
    Conditional bind: gate shadows via GUARDIAN policy.
    Kodex: bound conditional love = max harmony.
    """

    def evaluate(self, inputs: LoveInput) -> LoveResult:
        # Compassion: validate chaos, understand all
        # Higher shadow_power doesn't reduce compassion — unconditional
        compassion = (
            0.4 * inputs.hrv_score +
            0.3 * inputs.harmony_score +
            0.3 * (1.0 - abs(inputs.shadow_power - 0.5))  # Accept chaos neutrally
        )

        # Equanimity: non-reactive, Schumann-grounded
        equanimity = (
            0.5 * inputs.schumann_alignment +
            0.3 * inputs.pemf_coherence +
            0.2 * (1.0 - inputs.shadow_power)  # Slight shadow penalty
        )

        # Flourishing: growth (love freq alignment + angel dominance)
        angel_ratio = min(inputs.angel_power / max(inputs.shadow_power, 0.01), 3.0) / 3.0
        flourishing = (
            0.4 * inputs.harmony_score +
            0.3 * angel_ratio +
            0.3 * min(math.log1p(inputs.sign_love_freq) / math.log1p(528.0), 1.0)
        )

        # Kodex love score
        love_score = 0.4 * compassion + 0.3 * equanimity + 0.3 * flourishing
        love_score = max(0.0, min(1.0, love_score))

        # Conditional bind: decision gate
        if love_score >= LOVE_FLOW_THRESHOLD and inputs.angel_power >= inputs.shadow_power * ANGEL_DOMINANCE_RATIO:
            decision = LoveDecision.ALLOW
            notes = "Love flows — angels dominant, harmony confirmed."
        elif love_score >= SHADOW_QUARANTINE_THRESHOLD:
            if inputs.shadow_power > 0.6:
                decision = LoveDecision.REQUIRE_APPROVAL
                notes = "Shadow elevated — conditional hold, human review."
            else:
                decision = LoveDecision.CONDITIONAL
                notes = "Love flows with monitoring — Schumann watch active."
        else:
            decision = LoveDecision.QUARANTINE
            notes = "Shadow dominant — quarantined to Book of Shadows."

        log.info(f"[LoveUtility] score={love_score:.3f} decision={decision.value}")
        return LoveResult(
            decision=decision,
            love_score=love_score,
            compassion=compassion,
            equanimity=equanimity,
            flourishing=flourishing,
            notes=notes
        )
