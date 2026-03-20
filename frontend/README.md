# Frontend (Demo UI)

Minimal React + Vite frontend for Smart Attendance backend.

## Run

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

## Build

```powershell
npm.cmd run build
```

## Environment

Copy `.env.example` to `.env` and set:

- `VITE_API_BASE_URL` (default backend: `http://localhost:8000`)

## Demo flows

- Login with admin/operator/user credentials.
- Admin dashboard: system health, policy snapshot, operators.
- Operator dashboard: create user, enroll images, recognize image, view users and logs.
- User dashboard: view attendance history.
