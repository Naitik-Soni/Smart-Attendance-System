# Database

Main schema is in `main_app` SQLAlchemy models + Alembic migrations.

## Core Tables

- `organizations`
- `roles`
- `users`
- `user_profiles`
- `attendance_records`
- `attendance_logs`
- `face_images`
- `face_embeddings`
- `system_configs`
- `audit_logs`
- `revoked_tokens`

## Notes

- one attendance summary row per user per date
- event-level history is stored in `attendance_logs`
- policy values are loaded from `system_configs` with defaults in code
- run migration before startup: `alembic upgrade head`
