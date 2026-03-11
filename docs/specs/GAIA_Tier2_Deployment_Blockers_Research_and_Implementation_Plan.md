# GAIA Tier 2 — Deployment Blockers Research and Implementation Plan

## Purpose

Resolves Tier 2 deployment blockers:

1. Cross-host restore orchestration
2. Legal / jurisdiction engine and human approval UI
3. Real secure multi-instance federation
4. Large-scale merge governance engine

---

## Executive Decisions

- **Restore:** Kubernetes StatefulSet + CSI VolumeSnapshot (default) + CRIU (selective)
- **Approval:** OPA / Rego + Temporal + Next.js + TypeScript + WebAuthn step-up auth
- **Federation:** SPIFFE / SPIRE (identity) + libp2p (transport)
- **Governance:** CRDTs (collaborative workspace) + Raft-backed quorum (authoritative decisions)

---

## Restore Invariants

1. No restore without a signed checkpoint manifest.
2. No continuity claim without causal replay verification.
3. No cross-host promotion to trusted state until attestation and manifest hashes match.
4. CRIU restore is never the only recovery path.

---

## Federation Trust States

`UNTRUSTED` → `IDENTIFIED` → `ATTESTED` → `FEDERATED` → `DEGRADED` → `QUARANTINED`

---

## Immediate ADRs

1. **ADR-005:** hybrid restore architecture
2. **ADR-006:** OPA + Temporal + Next.js + WebAuthn
3. **ADR-007:** SPIFFE/SPIRE + libp2p
4. **ADR-008:** CRDT + quorum governance

---

## Cross-Repo Execution Order

- **Phase 0:** ADRs 005-008
- **Phase 1 (GAIA-Core):** restore manifest, policy schemas, federation envelopes, merge proposal schema
- **Phase 2 (GAIA-Server):** restore orchestrator, policy engine, SPIRE integration, governance APIs
- **Phase 3:** approval console UI, node-local operator views, trust-state UX
- **Phase 4 (GAIA-Meta):** federated topology control, global quorum, fleet restore catalog
