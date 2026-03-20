# Implementation Plan (Priority + Assumptions)

Date: 2026-03-18

## Assumptions

- Documentation is source of truth over current code state.
- Default recognition threshold rule is `confidence > 0.8`.
- Camera stream input may be 5 FPS, but recognition sampling is 1 FPS.
- Wall camera recognition candidates require face area ratio > 0.5.
- Attendance status uses dynamic DB-configured `MIN_TIME` and windows.
- Operational recognition-related retention is 35 days.
- External HR/LMS integrations are deferred.

## Priority Order

1. Policy and config foundation
2. Attendance rule engine (dynamic `MIN_TIME` + windows)
3. Recognition threshold and quality-gate enforcement
4. Camera ingestion policies (1 FPS sampling + wall area rule)
5. Storage plugin interface and backend registry
6. Retention and cleanup pipeline (35-day policy)
7. Performance and scalability validation

## Phase Plan

### Phase 1 (P0) - Config and Policy Foundation

- Add/normalize config keys in DB and service layer.
- Implement runtime policy loader/caching strategy.
- Add audit logging for policy updates.

Deliverables:
- policy config read/write APIs
- typed config contracts
- default bootstrap values

### Phase 2 (P0) - Attendance Computation Rules

- Persist all ENTRY/EXIT events.
- Maintain daily summary record per user.
- Compute total duration from first entry and last exit.
- Evaluate attendance by `MIN_TIME` and dynamic windows.

Deliverables:
- deterministic attendance calculation service
- unit and integration tests for edge cases

### Phase 3 (P1) - Enrollment and Recognition Hard Rules

- Enforce exactly one face per enrollment image.
- Enforce quality gate checks and rejection reasons.
- Apply strict threshold rule (`> 0.8`) from config.

Deliverables:
- validation and rejection taxonomy
- per-face decision metadata

### Phase 4 (P1) - Camera Ingestion Rules

- Implement 1 FPS sampling pipeline from stream sources.
- Enforce wall camera min face area ratio rule.
- Preserve source metadata for traceability.

Deliverables:
- ingestion adapters and policy-aware preprocessors
- camera mode integration tests

### Phase 5 (P1) - Pluggable Storage Layer

- Introduce storage interface abstraction.
- Add backend registry and enable/disable behavior.
- Implement local filesystem backend first.

Deliverables:
- storage adapter interface
- backend plugin lifecycle and health checks

### Phase 6 (P1) - Retention and Cleanup

- Implement scheduled retention task based on `retention.days`.
- Purge DB metadata and storage objects through plugin interface.
- Keep deletion audit logs.

Deliverables:
- purge service + scheduler
- retention verification tests

### Phase 7 (P2) - Performance and Scale Validation

- Define benchmark scenarios using realistic camera/profile assumptions.
- Measure latency and throughput at target scale bands.
- Produce tuning recommendations.

Deliverables:
- benchmark scripts and report
- SLO gap list and remediation backlog

## Acceptance Snapshot by Priority

P0 acceptance:
- Dynamic policy config works end-to-end.
- Attendance logic follows documented rules.

P1 acceptance:
- Recognition and camera rules enforced.
- Storage plugin and retention pipelines operational.

P2 acceptance:
- Latency/scalability metrics captured and documented.
