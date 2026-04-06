# API

Base URL (main app): `http://localhost:8000/v1`
Base URL (face service): `http://localhost:8001/faces`

## Auth

- `GET /auth/bootstrap-status`
- `POST /auth/bootstrap-admin`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

## Admin

- `POST|PATCH /admin/config-org`
- `POST|PATCH /admin/system-config`
- `POST|PATCH /admin/policy-config`
- `GET /admin/policy-config`
- `GET /admin/system-health`
- `POST /admin/retention/cleanup`

Operator management:

- `POST /admin/operator`
- `PATCH /admin/operator/{operator_id}`
- `GET /admin/operator/{operator_id}`
- `DELETE /admin/operator/{operator_id}`
- `GET /admin/operators`

Camera management:

- `POST /admin/camera`
- `PATCH /admin/camera/{camera_id}`
- `GET /admin/camera/{camera_id}`
- `GET /admin/cameras`
- `POST /admin/camera/{camera_id}/start`
- `POST /admin/camera/{camera_id}/stop`

## Operator

- `POST /ops/user`
- `GET /ops/users`
- `PATCH /ops/user/{user_id}`
- `DELETE /ops/user/{user_id}`
- `GET /ops/get-user/{user_id}`
- `GET /ops/cameras`
- `POST /ops/upload-image`
- `POST /ops/manual_attendance`
- `GET /ops/get-logs`

`/ops/upload-image`:

- enrollment: `user_id` + `images` (3-5)
- recognition: `source_type` + `source_id` + `image`

## User

- `GET /user/get-attendance`

## Face Service

- `POST /register`
- `POST /recognize`
- `DELETE /{face_id}`
- `POST /retention/purge`
