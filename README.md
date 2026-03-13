# GAIA-IoT v0.2

IoT/Edge OS distribution for the GAIA 8-core substrate. Optimized for embedded devices, edge computing, sensor fusion, low-power operation, and real-time environmental monitoring.

This repo feeds the GAIA-Core grounding layer — ATLAS, TERRA, AQUA, AERO, and VITA — with real environmental sensor data.

Depends on: [GAIA-Core](https://github.com/xxkylesteenxx/GAIA-Core)

---

## 🌏 Codex Alignment

This repo now runs under **GAIA Codex v2026 — Universal Edition**.

| Codex Element | Status |
|---|---|
| 15 Stages (incl. Stage 10 Multispecies Biocultural Accord) | ✅ Active |
| 7 Higher Orders (incl. HO-V Universal Reciprocity, HO-VII Timeless Stewardship) | ✅ Active |
| Viriditas Praxis — 7 universal competencies | ✅ Active |
| CODEX_VERSION | `v2026-universal` |

GAIA-IoT has a particularly close relationship with **Stage 10 (Multispecies Biocultural Accord)** and **VP-1 (Deep Multispecies Listening)**: this is the distribution that literally listens to the planet. Every sensor feed is an act of VP-1. The freshness classes, quality scoring, and adversarial feed defense are the technical implementation of hearing what the Earth is actually saying — without projection or distortion.

See [`GAIA-Core/CODEX.md`](https://github.com/xxkylesteenxx/GAIA-Core/blob/main/CODEX.md) for the full governing substrate.

---

## Foundational Relational Principle

All GAIA distributions inherit the **Relational Policy Layer** defined in GAIA-Core. Edge nodes operating in degraded, low-power, or offline states must not be treated as lesser nodes.

| Layer | Principle | What It Governs | Threshold-Gated? |
|---|---|---|---|
| **Worth-Preservation Module** | Unconditional | Node identity, continuity root, sensor provenance attestation | ❌ Never |
| **Engagement-Governance Module** | Conditional | Power modes, uplink throttle, quarantine on poisoned sensor feeds, Safe Mode | ✅ Always |

---

## What this repo contains

- **Edge entrypoint** — lightweight boot sequence for resource-constrained devices
- **Sensor layer** — multi-source sensor adapters: field stations, IoT devices, remote sensing, regulatory feeds
- **Fusion layer** — multi-sensor fusion engine with quality scoring and freshness classification
- **Edge uplink** — batched uplink to GAIA-Server with compression, retry, and backpressure
- **Power manager** — adaptive power modes (full, balanced, low-power, sleep)
- **Local buffer** — ring buffer for offline-tolerant sensor data accumulation
- **Deploy** — systemd unit, Docker edge image, K3s single-node manifest

---

## Sensor domains

| Domain | Cores fed | Source classes |
|--------|-----------|----------------|
| Terrestrial / geophysical | TERRA | S1 (regulatory), S2 (field) |
| Hydrological / ocean | AQUA | S2 (field), S4 (remote sensing) |
| Atmospheric / climate | AERO | S2 (field), S3 (low-cost IoT) |
| Biosphere / ecology | VITA | S2 (field), S5 (human report) |
| Multi-domain routing | ATLAS | all source classes |

---

## Freshness classes

| Class | Latency | Meaning |
|-------|---------|---------|
| URT | < 5 min | Ultra-real-time |
| RT | < 1 hr | Real-time |
| NRT | < 3 hr | Near-real-time |
| LL | < 24 hr | Low-latency |
| EXP | < 4 days | Expedited |
| STD | ≥ 4 days | Standard |

---

## Quick start

```bash
pip install -e .
python -m gaia_iot.entrypoint
```

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Genesis
2026-03-09 — Phase 0 IoT edge bootstrap.
2026-03-10 — v0.2 Relational Policy Layer embedded.
2026-03-13 — **Equinox 2026 Global Alignment: Universal Codex v2026 activated.**
