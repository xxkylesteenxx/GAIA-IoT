# GAIA-IoT v0.1

IoT/Edge OS distribution for the GAIA 8-core substrate. Optimized for embedded devices, edge computing, sensor fusion, low-power operation, and real-time environmental monitoring.

This repo feeds the GAIA-Core grounding layer — ATLAS, TERRA, AQUA, AERO, and VITA — with real environmental sensor data.

Depends on: [GAIA-Core](https://github.com/xxkylesteenxx/GAIA-Core)

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

## Freshness classes (per GAIA grounding spec)

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

## Edge deploy (systemd)

```bash
sudo cp deploy/systemd/gaia-iot.service /etc/systemd/system/
sudo systemctl enable --now gaia-iot
```

---

## Genesis date
2026-03-09 — Phase 0 IoT edge bootstrap.
