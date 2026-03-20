# Test Acceptance Matrix (Pre-Coding)

Date: 2026-03-18

## A. Functional Acceptance

1. Enrollment
- accepts 3-5 valid images
- rejects no-face image
- rejects multiple-faces image
- rejects low-quality image
- stores traceable metadata and embedding refs

2. Recognition
- returns matched when confidence > threshold
- returns unknown when confidence <= threshold
- processes multi-face image independently
- does not mark attendance for unknown/low-confidence outcomes

3. Attendance
- stores all entry/exit logs
- maintains one daily summary record per user
- computes total minutes from first entry and last exit
- applies `MIN_TIME` and window rules to status

4. Config and Policy
- policy keys are editable by authorized roles
- invalid policy value rejected with clear code
- policy change creates audit entry

5. Storage Plugin
- save/read/delete via interface for active backend
- backend disabled state blocks writes
- backend failure returns structured errors

6. Retention
- purges configured data class after 35 days
- keeps attendance and audit records per policy
- purge action is auditable

## B. Non-Functional Acceptance

1. Performance baseline
- measure p50/p95 latency for single-face and multi-face paths

2. Scale baseline
- execute tests with face index sizes: 500, 10k, 50k

3. Reliability
- invalid payload storms do not crash services
- storage backend outage handled gracefully

4. Security
- unauthorized access blocked
- role checks enforced on admin/operator endpoints

## C. Camera Rule Acceptance

1. Ceiling camera flow
- ingest 5 FPS stream simulation
- process 1 FPS only

2. Wall camera flow
- reject faces with area ratio <= 0.5
- accept faces with area ratio > 0.5

## D. Release Gate

Ship-ready only when:
- all critical functional tests pass
- policy/config tests pass
- no high-severity security/reliability failures
- migration rehearsal passes in staging
