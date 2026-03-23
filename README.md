# Smart Attendance System

Production-ready attendance platform using face recognition.

## Architecture

- `main_app`: auth, roles, admin/ops APIs, attendance, policy and camera config
- `face_service`: face enrollment and recognition
- `frontend`: React UI for Admin/Operator/User roles

## Ports

- `main_app`: `http://localhost:8000`
- `face_service`: `http://localhost:8001`
- `frontend` (Vite): `http://localhost:5173` (or next free port)

## Prerequisites

- Python `3.10+`
- Node.js `18+`
- PostgreSQL `14+`
- Git

---

## 1) Clone and open project

```bash
git clone <your-repo-url>
cd Smart-Attendance-System
```

---

## 2) Create virtual environment and install backend dependencies

### Windows PowerShell

```powershell
python -m venv .sasenv
.\.sasenv\Scripts\Activate.ps1
pip install -r .\main_app\requirements.txt
pip install -r .\face_service\requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .sasenv
source .sasenv/bin/activate
pip install -r ./main_app/requirements.txt
pip install -r ./face_service/requirements.txt
```

---

## 3) Setup PostgreSQL database

Create DB user and database:

```sql
CREATE USER sas_user WITH PASSWORD 'StrongDbPass123';
CREATE DATABASE smart_attendance OWNER sas_user;
GRANT ALL PRIVILEGES ON DATABASE smart_attendance TO sas_user;
```

---

## 4) Configure environment files

### `main_app/.env`

Copy from template:

- Windows:
```powershell
Copy-Item .\main_app\.env.example .\main_app\.env
```
- Linux/macOS:
```bash
cp ./main_app/.env.example ./main_app/.env
```

Set at minimum:

```env
DATABASE_URL=postgresql://sas_user:StrongDbPass123@localhost:5432/smart_attendance
AUTO_INIT_DB=false
SECRET_KEY=replace-with-a-strong-random-secret
FACE_SERVICE_URL=http://localhost:8001
```

### `face_service/.env`

Copy from template and adjust if needed:

- Windows:
```powershell
Copy-Item .\face_service\.env.example .\face_service\.env
```
- Linux/macOS:
```bash
cp ./face_service/.env.example ./face_service/.env
```

---

## 5) Run DB migrations (mandatory)

### Windows PowerShell

```powershell
cd .\main_app
$env:PYTHONPATH='.'
..\.sasenv\Scripts\python.exe -m alembic upgrade head
```

If the relative path fails in your shell, use absolute path:

```powershell
C:\path\to\Smart-Attendance-System\.sasenv\Scripts\python.exe -m alembic upgrade head
```

### Linux/macOS

```bash
cd ./main_app
export PYTHONPATH=.
../.sasenv/bin/python -m alembic upgrade head
```

---

## 6) Start backend services

Open separate terminals.

### Terminal A: face_service

Windows:
```powershell
cd .\face_service
$env:PYTHONPATH='.'
C:\path\to\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Linux/macOS:
```bash
cd ./face_service
export PYTHONPATH=.
../.sasenv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Terminal B: main_app

Windows:
```powershell
cd .\main_app
$env:PYTHONPATH='.'
C:\path\to\Smart-Attendance-System\.sasenv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Linux/macOS:
```bash
cd ./main_app
export PYTHONPATH=.
../.sasenv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 7) Start frontend

### Terminal C

```bash
cd frontend
npm install
npm run dev
```

Ensure `frontend/.env` has:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 8) First-time startup behavior (important)

If no Admin exists, login is blocked and UI redirects to:

- `/setup-admin`

You must create the first Admin there.  
After success, system signs in and opens Admin dashboard.

---

## 9) Health checks

- `GET http://localhost:8000/health`
- `GET http://localhost:8001/health`
- `GET http://localhost:8000/metrics`
- `GET http://localhost:8001/metrics`

---

## 10) Common issues

- `ADMIN_SETUP_REQUIRED` on login:
  - Create first admin at `/setup-admin`.

- Migration fails:
  - Recheck `DATABASE_URL` and DB credentials.

- CORS/browser API errors:
  - Verify `VITE_API_BASE_URL` points to `main_app`.
  - Verify `main_app` CORS allows frontend origin.

- Camera worker not running:
  - Register camera from Admin `Camera Config`.
  - Start worker using `Start` action.
