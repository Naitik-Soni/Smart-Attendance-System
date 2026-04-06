# Setup

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## 1. Install backend deps

```powershell
python -m venv .sasenv
.\.sasenv\Scripts\Activate.ps1
pip install -r .\main_app\requirements.txt
pip install -r .\face_service\requirements.txt
```

## 2. Configure env files

```powershell
Copy-Item .\main_app\.env.example .\main_app\.env
Copy-Item .\face_service\.env.example .\face_service\.env
```

Set in `main_app/.env`:

```env
DATABASE_URL=postgresql://sas_user:StrongDbPass123@localhost:5432/smart_attendance
AUTO_INIT_DB=false
SECRET_KEY=replace-with-a-strong-random-secret
FACE_SERVICE_URL=http://localhost:8001
```

Set in `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 3. Run migrations

```powershell
cd .\main_app
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m alembic upgrade head
```

## 4. Start services

Face service:

```powershell
cd .\face_service
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Main app:

```powershell
cd .\main_app
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd .\frontend
npm.cmd install
npm.cmd run dev
```

## 5. First login

If no admin exists, app redirects to `/setup-admin`.
Create the first admin, then sign in.
