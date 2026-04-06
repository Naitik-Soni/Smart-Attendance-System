# Smart Attendance System

Production-ready attendance platform with face recognition, role-based workflows, and policy-driven configuration.

## Architecture

- `main_app` (FastAPI): authentication, RBAC, admin/operator/user APIs, attendance, policies, camera config, audit logs
- `face_service` (FastAPI): face enrollment, recognition, embeddings, unknown capture, retention purge
- `frontend` (React + Vite): UI for Admin, Operator, and User roles
- `storage`: local face images and embedding index artifacts

## Default Ports

- `main_app`: `http://localhost:8000`
- `face_service`: `http://localhost:8001`
- `frontend`: `http://localhost:5173`

## Prerequisites

- Python `3.10+`
- Node.js `18+`
- PostgreSQL `14+`
- Git

## Setup

### 1. Clone and enter repository

```bash
git clone <your-repo-url>
cd Smart-Attendance-System
```

### 2. Create virtual environment and install backend dependencies

Windows PowerShell:

```powershell
python -m venv .sasenv
.\.sasenv\Scripts\Activate.ps1
pip install -r .\main_app\requirements.txt
pip install -r .\face_service\requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .sasenv
source .sasenv/bin/activate
pip install -r ./main_app/requirements.txt
pip install -r ./face_service/requirements.txt
```

### 3. Prepare PostgreSQL

```sql
CREATE USER sas_user WITH PASSWORD 'StrongDbPass123';
CREATE DATABASE smart_attendance OWNER sas_user;
GRANT ALL PRIVILEGES ON DATABASE smart_attendance TO sas_user;
```

### 4. Configure environment files

Create env files from templates.

Windows:

```powershell
Copy-Item .\main_app\.env.example .\main_app\.env
Copy-Item .\face_service\.env.example .\face_service\.env
```

Linux/macOS:

```bash
cp ./main_app/.env.example ./main_app/.env
cp ./face_service/.env.example ./face_service/.env
```

Set minimum required values in `main_app/.env`:

```env
DATABASE_URL=postgresql://sas_user:StrongDbPass123@localhost:5432/smart_attendance
AUTO_INIT_DB=false
SECRET_KEY=replace-with-a-strong-random-secret
FACE_SERVICE_URL=http://localhost:8001
```

### 5. Run database migrations

Windows PowerShell:

```powershell
cd .\main_app
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m alembic upgrade head
```

Linux/macOS:

```bash
cd ./main_app
export PYTHONPATH=.
../.sasenv/bin/python -m alembic upgrade head
```

### 6. Start backend services

Open separate terminals.

Face service:

```powershell
cd .\face_service
$env:PYTHONPATH='.'
C:\path\to\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Main app:

```powershell
cd .\main_app
$env:PYTHONPATH='.'
C:\path\to\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Set `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## First Startup Flow

If no admin exists, login is blocked and frontend redirects to `/setup-admin`.
Create the first admin there, then continue to the Admin dashboard.

## Health and Metrics

- `GET http://localhost:8000/health`
- `GET http://localhost:8001/health`
- `GET http://localhost:8000/metrics`
- `GET http://localhost:8001/metrics`

## Common Issues

- `ADMIN_SETUP_REQUIRED` on login: create first admin at `/setup-admin`
- migration errors: verify `DATABASE_URL`, DB host, and credentials
- CORS/API issues: verify `VITE_API_BASE_URL` and backend CORS config
- camera worker not running: register camera and start worker from Admin Camera page
