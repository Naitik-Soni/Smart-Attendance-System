# Main API Contract (Aligned with Current Requirements)

Base path: `/v1`
Envelope:
- `success`
- `code`
- `message`
- `data`
- `meta`
- `errors`

## 1. Auth APIs

### `POST /v1/auth/login`
Request:
```json
{
  "user_id": "admin_01",
  "password": "StrongPass123"
}
```

### `POST /v1/auth/refresh`
### `POST /v1/auth/logout`

## 2. Admin APIs

### `POST|PATCH /v1/admin/config-org`
Purpose:
- Organization details
- Attendance policy defaults
- Retention defaults

### `POST|PATCH /v1/admin/system-config`
Purpose:
- Camera and ingestion policy
- Recognition and quality policy
- Storage backend policy

Expected policy keys managed via config APIs:
- `recognition.threshold` (default 0.8, decision rule is confidence > threshold)
- `attendance.min_time_minutes`
- `attendance.windows`
- `retention.days` (default 35)
- `camera.stream.sampling_fps` (default 1)
- `camera.wall.min_face_area_ratio` (default 0.5)

### `GET /v1/admin/system-health`
### `POST /v1/admin/operator`
### `PATCH /v1/admin/operator/{operator_id}`
### `GET /v1/admin/operator/{operator_id}`
### `DELETE /v1/admin/operator/{operator_id}`
### `GET /v1/admin/operators`

## 3. Operations APIs

### `POST /v1/ops/user`
### `GET /v1/ops/users`
### `PATCH /v1/ops/user/{user_id}`
### `DELETE /v1/ops/user/{user_id}`
### `GET /v1/ops/get-user/{user_id}`

### `POST /v1/ops/upload-image`
Content type: `multipart/form-data`

Modes:
1. Enrollment mode
- required: `user_id`, `images[]` (3-5)

2. Recognition mode
- required: `source_type`, `source_id`, `timestamp`, `image`
- `source_type` supports `ceiling_camera`, `wall_camera`, `upload_image`

Decision notes:
- attendance is marked only when recognition result is matched and confidence > threshold
- wall camera eligibility includes face area ratio > 0.5

Sample recognition failure fragment:
```json
{
  "success": false,
  "code": "WALL_FACE_RATIO_TOO_LOW",
  "message": "Face area ratio below configured wall-camera minimum",
  "data": null,
  "meta": {
    "min_ratio": 0.5,
    "observed_ratio": 0.42
  },
  "errors": []
}
```

### `POST /v1/ops/manual_attendance`
Rules:
- store all entry/exit logs
- update daily summary using first entry/last exit
- apply `MIN_TIME` from dynamic config

### `GET /v1/ops/get-logs`

## 4. User APIs

### `GET /v1/user/get-attendance`
Returns attendance summary records.

## 5. Error Code Contract (Core)

Recognition/enrollment errors:
- `NO_FACE_DETECTED`
- `MULTIPLE_FACES_IN_ENROLLMENT`
- `IMAGE_QUALITY_TOO_LOW`
- `INVALID_IMAGE`
- `MATCH_BELOW_THRESHOLD`
- `WALL_FACE_RATIO_TOO_LOW`

Policy/config errors:
- `POLICY_KEY_NOT_FOUND`
- `POLICY_VALUE_INVALID`
- `POLICY_UPDATE_FORBIDDEN`

Storage errors:
- `STORAGE_BACKEND_UNAVAILABLE`
- `STORAGE_WRITE_FAILED`
- `STORAGE_READ_FAILED`

Attendance errors:
- `ATTENDANCE_WINDOW_VIOLATION`
- `ATTENDANCE_MIN_TIME_NOT_MET`
