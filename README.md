# Smart-Attendance-System

Smart attendance platform using face recognition with:
- `main_app` (business APIs, auth, attendance, policy config)
- `face_service` (face enrollment, recognition, vector matching)

## Production Status

Core production-oriented foundations are implemented:
- policy-driven thresholds and quality gates
- strict enrollment validation
- dynamic attendance rule engine (`MIN_TIME`, windows, late grace)
- pluggable image storage adapter (local backend first)
- retention cleanup endpoints (filesystem + metadata)
- Alembic migration for new attendance status field

Refer to runbook:
- `documentation/Production Runbook.md`
