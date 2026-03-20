# Policies and Rules by Task

Date: 2026-03-18

## 1. Enrollment Policy

Rules:
- Each enrollment image must contain exactly one face.
- Required enrollment image count: 3-5 per user.
- Reject image if no face, multiple faces, or poor quality.
- Face landmarks/features must be clearly visible.

Outputs:
- Accepted image metadata
- rejection reason code for failed images

## 2. Recognition Policy

Rules:
- Match only when `confidence > threshold`.
- Default threshold is `0.8`, configurable via system config.
- Low confidence and unknown outcomes must not mark attendance.

Outputs:
- per-face status: matched/unknown/rejected
- confidence and decision reason

## 3. Camera Ingestion Policy

Ceiling/top camera:
- Source stream may be 5 FPS.
- Recognition sampling rate is 1 FPS.

Wall camera:
- Same 1 FPS sampling rule.
- Face area ratio must be > 50% of frame for recognition eligibility.

Outputs:
- source metadata with sampling timestamp
- skipped-frame counters and reasons

## 4. Attendance Policy

Rules:
- Keep all entry/exit events.
- One daily attendance summary per user per date.
- Daily total duration = last exit - first entry.
- Attendance result is determined by configurable `MIN_TIME`.
- Attendance windows are dynamic and user-managed in DB.

Outputs:
- attendance_logs (event level)
- attendance_records (daily summary)

## 5. Retention Policy

Rules:
- Operational recognition-related data retention is 35 days.
- Purge policy must remove expired DB metadata and storage objects.
- All purge actions must be auditable.

Outputs:
- purge execution logs
- deleted artifacts report

## 6. Storage Plugin Policy

Rules:
- All image persistence/retrieval must go through storage interface.
- Backend plugins can be enabled/disabled per config.
- One backend can be default active backend.
- Plugin failure must degrade gracefully with structured errors.

Outputs:
- backend status and health
- deterministic artifact references

## 7. Configuration Governance Policy

Rules:
- Policy values are DB-driven and editable by authorized roles only.
- Changes to threshold, attendance windows, `MIN_TIME`, retention, and camera rules are auditable.
- Runtime services should reload policy safely without service restart where feasible.

Outputs:
- config change audit entries
- policy version metadata
