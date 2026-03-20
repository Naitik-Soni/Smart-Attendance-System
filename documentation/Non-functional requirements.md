# Non-Functional Requirements (NFR)

These define how well the system must behave.

## NFR-1 Performance and Latency

- Target single-image recognition latency: <= 200 ms (target SLO).
- Target multi-face image latency: <= 500 ms (target SLO).
- System must support concurrent requests.

Camera workload assumptions:
- Stream source is 5 FPS, but recognition sampling is 1 image/second per camera.
- Wall camera face eligibility requires visible face area > 50% of frame.

## NFR-2 Scalability

The system should scale for:
- 10,000 to 50,000 enrolled face identities (upper planning range).
- Average practical active load around 500 users in common operating context.
- One to many cameras per organization.

Architecture constraints:
- No hard coupling to single camera/location.
- Keep service boundaries ready for horizontal scaling.

## NFR-3 Accuracy and Reliability

- Use embedding similarity matching, not closed-set classification.
- Default match threshold must be > 0.8 and configurable.
- Prefer false negatives over false positives.
- Attendance must never be marked for low-confidence/unknown matches.
- Enrollment quality gates are mandatory.

## NFR-4 Availability and Fault Tolerance

The system must gracefully handle:
- no face detected,
- multiple faces in enrollment,
- corrupted/invalid image payload,
- storage backend/plugin unavailability.

Failure behavior:
- Recognition failure must not crash the service.
- API responses must be structured and actionable.

## NFR-5 Security

- All operational/admin APIs must be authenticated and role-protected.
- Embeddings and face metadata are sensitive data.
- Storage plugin interfaces must enforce secure access patterns.
- Configuration changes (threshold, windows, retention) must be auditable.

## NFR-6 Privacy and Data Retention

- Retention policy: keep operational recognition-related data for up to 35 days (current policy).
- No cross-frame identity tracking requirement.
- Keep clear separation between capture, recognition, attendance, and storage concerns.
- Storage layer must allow policy-driven retention/deletion.

## NFR-7 Maintainability and Extensibility

- Keep modular separation between business APIs and ML service.
- New input modes should plug in without rewriting core business logic.
- Storage backends must be pluggable through a common interface.
- Threshold and attendance policy must be config-driven (DB/application config).

## NFR-8 Observability and Operations

- Structured logs for recognition, attendance decisions, and policy applications.
- Persist confidence scores and decision reason metadata.
- Track error rate, rejection rate, and latency metrics.
- Keep audit trail for config and role-sensitive actions.
