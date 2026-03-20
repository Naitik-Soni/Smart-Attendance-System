# Functional Requirements (FR)

These define what the system must do. Documentation is the source of truth.

## FR-1 User and Identity Management

The system shall:
- Create users (employee/student) with unique user ID.
- Deactivate/delete users with soft-delete support.
- Support role-based actors (admin/operator/user).
- Store user metadata (name, department, role, email, employee code).
- Isolate data by organization/tenant.

## FR-2 Face Enrollment and Quality Gate

The system shall:
- Accept 3-5 enrollment images per user (configurable by policy if needed later).
- Enforce exactly one face per enrollment image.
- Reject enrollment images for:
- no face,
- multiple faces,
- low quality.
- Generate normalized embeddings and register them against the user.
- Support re-enrollment (replace/update enrollment set).

Quality requirements for enrollment input:
- Image resolution must be sufficient for recognition.
- Face landmarks/features must be clearly visible.
- Face crop must not be too small for reliable embedding.
- Final numeric thresholds are defined in policy/config.

## FR-3 Image Ingestion Modes

The system shall support:
- Manual upload image mode.
- Ceiling/top continuous camera mode.
- Wall camera mode.

All ingestion requests shall carry:
- `source_type`
- `source_id`
- `timestamp`
- image payload

Mode-specific rule:
- For streaming source input, process one frame per second for recognition.

## FR-4 Face Recognition

For each received image/frame, the system shall:
- Detect zero or more faces.
- Process each detected face independently.
- Match embeddings against enrolled faces/users.
- Return match result per face:
- `matched` with user ID and confidence, or
- `unknown` with unknown identifier.

Recognition threshold policy:
- Default threshold is strictly greater than `0.8`.
- Threshold must be configurable in application/system config.

## FR-5 Attendance Logic

The system shall:
- Mark attendance only for recognized users above configured threshold.
- Store all entry and exit events as immutable logs.
- Maintain one daily attendance summary record per user per day.
- Compute worked duration as `last_exit - first_entry` for that day.
- Evaluate attendance status using configurable `MIN_TIME`.
- Support dynamic user-configurable attendance windows/policies from DB.

## FR-6 Multi-Face Handling

The system shall:
- Handle multiple faces in one image.
- Evaluate each face independently.
- Mark attendance only for valid recognized faces.
- Keep unknown/low-confidence faces as non-attendance outcomes.

## FR-7 Traceability, Audit, and History

The system shall:
- Log all recognition attempts.
- Log failed/unknown/low-confidence events.
- Preserve traceability chain: image -> recognition -> attendance.
- Provide attendance history query APIs.
- Retain recognition/related operational data for up to 35 days (current policy).

## FR-8 Storage Abstraction (Pluggable)

The system shall:
- Provide a storage interface abstraction for image persistence/retrieval.
- Support plugin-like add/remove storage backends.
- Keep storage backend choice configurable without changing business logic.

Examples of backends (current/future):
- local filesystem
- object storage
- cloud provider storage

## FR-9 External Integration

External integrations/exports are out of current priority and deferred.
