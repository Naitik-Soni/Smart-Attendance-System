# Operations

## Health Checks

- `GET http://localhost:8000/health`
- `GET http://localhost:8001/health`
- `GET http://localhost:8000/metrics`
- `GET http://localhost:8001/metrics`

## Retention

- Face service purge: `POST /faces/retention/purge`
- Main app metadata cleanup: `POST /v1/admin/retention/cleanup`

Script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\ops\run_retention.ps1
```

## Quick Troubleshooting

- login blocked: create first admin on `/setup-admin`
- 401 errors: verify token and role
- face calls failing: verify `FACE_SERVICE_URL` and face service health
- camera worker issues: register camera and start worker from Admin Cameras page
