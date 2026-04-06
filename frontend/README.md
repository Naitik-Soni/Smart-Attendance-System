# Frontend (React + Vite)

UI layer for Smart Attendance System.

## Purpose

- role-based navigation and guarded routes
- admin/operator/user workflows
- API integration with `main_app`

## Run (Development)

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

## Build

```powershell
npm.cmd run build
```

## Preview Built App

```powershell
npm.cmd run preview
```

## Environment

Set `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Implemented UI Flows

- login and bootstrap-admin redirect
- admin pages: overview, operators, policies, cameras
- operator pages: users, enrollment, scan
- user page: attendance history
