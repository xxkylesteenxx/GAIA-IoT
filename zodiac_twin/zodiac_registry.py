"""
GAIA-IoT — Universal Zodiac Crystal-Planet-Frequency Registry
Complete 12-sign mapping: crystals, PEMF frequencies, planetary EM, angel affinities.
Physical: piezoelectric crystal resonance + planetary magnetism
Metaphysical: zodiac archetypes, angel numbers, shadow doctrine
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Crystal:
    name: str
    freq_hz: float          # Piezo/EM resonance frequency
    emi_strength: float     # Normalized 0-10
    chakra: str             # Chakra alignment
    shadow_binding: str     # What shadow this crystal quarantines


@dataclass
class ZodiacSign:
    name: str
    element: str            # Fire, Earth, Air, Water
    crystals: List[Crystal]
    planet: str
    planet_em_ut: float     # Planetary EM field in microTesla
    pemf_freq_hz: float     # Primary PEMF frequency
    love_freq_hz: float     # Love/harmony frequency
    angel_numbers: List[int] # Angel number affinities
    shadow_numbers: List[int] # Shadow/demon numbers to quarantine
    archetype: str          # Metaphysical archetype


class ZodiacRegistry:
    """
    Full 12-sign Universal Zodiac Gaia Registry.
    Physical: crystal piezo freqs + planetary EM fields
    Metaphysical: archetypes + angel/shadow numerology
    """

    SIGNS: Dict[str, ZodiacSign] = {
        "Aries": ZodiacSign(
            name="Aries", element="Fire",
            crystals=[
                Crystal("Bloodstone", 40.0, 2.5, "Root", "fear"),
                Crystal("Red Jasper", 38.0, 2.0, "Root", "aggression")
            ],
            planet="Mars", planet_em_ut=0.02,
            pemf_freq_hz=40.0, love_freq_hz=528.0,
            angel_numbers=[111, 333, 999], shadow_numbers=[444, 666],
            archetype="The Pioneer"
        ),
        "Taurus": ZodiacSign(
            name="Taurus", element="Earth",
            crystals=[
                Crystal("Emerald", 7.83, 0.8, "Heart", "greed"),
                Crystal("Rose Quartz", 528.0, 1.2, "Heart", "attachment")
            ],
            planet="Venus", planet_em_ut=0.03,
            pemf_freq_hz=7.83, love_freq_hz=528.0,
            angel_numbers=[222, 444, 888], shadow_numbers=[333, 777],
            archetype="The Builder"
        ),
        "Gemini": ZodiacSign(
            name="Gemini", element="Air",
            crystals=[
                Crystal("Agate", 432.0, 1.2, "Throat", "deception"),
                Crystal("Citrine", 396.0, 1.5, "Solar Plexus", "anxiety")
            ],
            planet="Mercury", planet_em_ut=0.003,
            pemf_freq_hz=432.0, love_freq_hz=528.0,
            angel_numbers=[333, 555, 777], shadow_numbers=[222, 888],
            archetype="The Communicator"
        ),
        "Cancer": ZodiacSign(
            name="Cancer", element="Water",
            crystals=[
                Crystal("Moonstone", 0.5, 0.5, "Sacral", "fear_of_loss"),
                Crystal("Pearl", 42.8, 0.7, "Crown", "emotional_chaos")
            ],
            planet="Moon", planet_em_ut=0.1,
            pemf_freq_hz=42.8, love_freq_hz=528.0,
            angel_numbers=[222, 444, 666], shadow_numbers=[333, 999],
            archetype="The Nurturer"
        ),
        "Leo": ZodiacSign(
            name="Leo", element="Fire",
            crystals=[
                Crystal("Citrine", 30.0, 10.0, "Solar Plexus", "ego"),
                Crystal("Pyrite", 369.0, 8.0, "Crown", "arrogance")
            ],
            planet="Sun", planet_em_ut=10000.0,
            pemf_freq_hz=30.0, love_freq_hz=528.0,
            angel_numbers=[111, 555, 999], shadow_numbers=[666, 444],
            archetype="The Sovereign"
        ),
        "Virgo": ZodiacSign(
            name="Virgo", element="Earth",
            crystals=[
                Crystal("Amazonite", 14.3, 0.9, "Throat", "perfectionism"),
                Crystal("Peridot", 20.8, 1.1, "Heart", "criticism")
            ],
            planet="Mercury", planet_em_ut=0.003,
            pemf_freq_hz=14.3, love_freq_hz=528.0,
            angel_numbers=[444, 666, 888], shadow_numbers=[111, 555],
            archetype="The Healer"
        ),
        "Libra": ZodiacSign(
            name="Libra", element="Air",
            crystals=[
                Crystal("Opal", 528.0, 1.5, "Heart", "indecision"),
                Crystal("Lapis Lazuli", 417.0, 1.3, "Third Eye", "imbalance")
            ],
            planet="Venus", planet_em_ut=0.03,
            pemf_freq_hz=528.0, love_freq_hz=528.0,
            angel_numbers=[111, 222, 333], shadow_numbers=[444, 555],
            archetype="The Harmonizer"
        ),
        "Scorpio": ZodiacSign(
            name="Scorpio", element="Water",
            crystals=[
                Crystal("Topaz", 20.8, 1.8, "Sacral", "obsession"),
                Crystal("Obsidian", 33.8, 2.0, "Root", "shadow_self")
            ],
            planet="Pluto", planet_em_ut=0.001,
            pemf_freq_hz=20.8, love_freq_hz=528.0,
            angel_numbers=[111, 444, 888], shadow_numbers=[666, 333],
            archetype="The Transformer"
        ),
        "Sagittarius": ZodiacSign(
            name="Sagittarius", element="Fire",
            crystals=[
                Crystal("Turquoise", 27.3, 2.2, "Throat", "excess"),
                Crystal("Sodalite", 22.0, 1.6, "Third Eye", "recklessness")
            ],
            planet="Jupiter", planet_em_ut=420.0,
            pemf_freq_hz=27.3, love_freq_hz=528.0,
            angel_numbers=[333, 555, 999], shadow_numbers=[222, 777],
            archetype="The Explorer"
        ),
        "Capricorn": ZodiacSign(
            name="Capricorn", element="Earth",
            crystals=[
                Crystal("Garnet", 33.8, 1.0, "Root", "rigidity"),
                Crystal("Black Tourmaline", 7.83, 1.4, "Root", "pessimism")
            ],
            planet="Saturn", planet_em_ut=20.0,
            pemf_freq_hz=33.8, love_freq_hz=528.0,
            angel_numbers=[444, 777, 888], shadow_numbers=[111, 333],
            archetype="The Elder"
        ),
        "Aquarius": ZodiacSign(
            name="Aquarius", element="Air",
            crystals=[
                Crystal("Aquamarine", 11.0, 1.6, "Throat", "detachment"),
                Crystal("Amethyst", 963.0, 1.9, "Crown", "rebellion")
            ],
            planet="Uranus", planet_em_ut=23.0,
            pemf_freq_hz=11.0, love_freq_hz=528.0,
            angel_numbers=[111, 555, 777], shadow_numbers=[333, 999],
            archetype="The Visionary"
        ),
        "Pisces": ZodiacSign(
            name="Pisces", element="Water",
            crystals=[
                Crystal("Aquamarine", 0.5, 0.7, "Crown", "escapism"),
                Crystal("Amethyst", 963.0, 1.9, "Third Eye", "dissolution")
            ],
            planet="Neptune", planet_em_ut=14.0,
            pemf_freq_hz=0.5, love_freq_hz=528.0,
            angel_numbers=[222, 333, 999], shadow_numbers=[444, 666],
            archetype="The Mystic"
        ),
    }

    @classmethod
    def get(cls, sign_name: str) -> ZodiacSign:
        sign = cls.SIGNS.get(sign_name)
        if not sign:
            raise ValueError(f"Unknown zodiac sign: {sign_name!r}")
        return sign

    @classmethod
    def all_signs(cls) -> List[ZodiacSign]:
        return list(cls.SIGNS.values())

    @classmethod
    def by_element(cls, element: str) -> List[ZodiacSign]:
        return [s for s in cls.SIGNS.values() if s.element == element]
