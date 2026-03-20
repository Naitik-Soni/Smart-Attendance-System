# Production Runbook

Date: 2026-03-18

## 1. Environment Preparation

Use:
- `main_app/.env.prod.example`
- `face_service/.env.prod.example`

Key requirements:
- valid Postgres credentials
- `AUTO_INIT_DB=false` for `main_app`
- secure `SECRET_KEY`
- persistent storage paths for face artifacts and FAISS files

## 2. Database Migration

Run in `main_app` with `.sasenv`:

```powershell
$env:PYTHONPATH='.'
$env:DATABASE_URL='postgresql://<user>:<password>@<host>:5432/<db>'
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe -m alembic upgrade head
```

If credentials are wrong, migration will fail before app start. Fix DB URL and rerun.

## 3. Service Startup

Face service:

```powershell
cd face_service
$env:PYTHONPATH='.'
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Main service:

```powershell
cd main_app
$env:PYTHONPATH='.'
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 4. Post-Deploy Validation

- `GET /health` on both services.
- `GET /metrics` on both services.
- Admin login and token flow.
- `GET /v1/admin/policy-config`.
- Enroll face with 3 valid images.
- Recognition request with source metadata.
- Verify attendance and audit log entries.

## 5. Retention Operations

Filesystem cleanup endpoint (`face_service`):
- `POST /faces/retention/purge`

Metadata cleanup endpoint (`main_app`):
- `POST /v1/admin/retention/cleanup`

Schedule both daily (off-peak).

Windows scheduler option:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ops\run_retention.ps1
```

Scheduled time (locked):
- Daily at `06:00 AM` local time.

## 6. Load and Latency Baseline

Run quick baseline from project root:

```powershell
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe scripts\load\main_app_load_test.py --base-url http://localhost:8000 --requests 1000 --concurrency 50
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe scripts\load\face_service_load_test.py --base-url http://localhost:8001 --requests 1000 --concurrency 50
```

Record p50/p95 latency outputs per release.

## 7. Rollback

DB rollback:

```powershell
cd main_app
$env:PYTHONPATH='.'
C:\Users\baps\Documents\Projects\Smart-Attendance-System\.sasenv\Scripts\python.exe -m alembic downgrade -1
```

Service rollback:
- deploy previous release artifacts and restart services.

## Go-Live Window

- Preferred go-live slot: `12:00 AM` (date-change boundary, local time).
