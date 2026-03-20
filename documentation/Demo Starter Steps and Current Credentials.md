# Demo Starter Steps and Current Credentials

Date: 2026-03-19
Mode: Localhost demo

## Current Credentials and Runtime Values

### Database
- `DATABASE_URL=postgresql://postgres:1234@localhost:5433/smart_attendance`

### Main App Security
- `SECRET_KEY=YgLZ1IRQOmS07Asc8NszSWj_iDktYRuJ_lVNI2NB_qRvcAjZALSzdsyBOWZlK3Uwf-IrYBN3LA9QA894Ur0KYA`
- Admin user (bootstrap):
- `user_id=admin1`
- `password=StrongPass123`

### Service URLs
- Main app: `http://127.0.0.1:8000`
- Face service: `http://127.0.0.1:8001`

### Storage
- `STORAGE_ROOT=../storage` (shared local folder from service directories)

## One-Time Setup (already done)

1. Postgres database created: `smart_attendance`
2. Alembic migrations applied to head
3. Required folders created under `storage/`

## Start Services

### Terminal 1: face_service
```powershell
cd C:\Users\baps\Documents\Projects\Smart-Attendance-System\face_service
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Terminal 2: main_app
```powershell
cd C:\Users\baps\Documents\Projects\Smart-Attendance-System\main_app
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Open Swagger

- Main app: `http://127.0.0.1:8000/docs`
- Face service: `http://127.0.0.1:8001/docs`

## Demo Flow (API Sequence)

1. `POST /v1/auth/bootstrap-admin` (run once; skip if already created)
2. `POST /v1/auth/login` as admin
3. Authorize Swagger with admin bearer token
4. `POST /v1/admin/operator` (create operator)
5. Login as operator
6. `POST /v1/ops/user` (create employee/user)
7. `POST /v1/ops/upload-image` with `user_id + images[]` (3-5 images) for enrollment
8. `POST /v1/ops/upload-image` with `source_type/source_id/image` for recognition
9. `GET /v1/user/get-attendance`
10. `GET /v1/ops/get-logs`

## Retention and Schedule

- Retention script: `scripts/ops/run_retention.ps1`
- Planned schedule: daily at `06:00 AM`
- Planned go-live/demo window: `12:00 AM`

## Note

If bcrypt/passlib error appears again, run:
```powershell
cd C:\Users\baps\Documents\Projects\Smart-Attendance-System
.\.sasenv\Scripts\python.exe -m pip install "bcrypt==4.0.1"
```
