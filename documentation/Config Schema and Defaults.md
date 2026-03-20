# Configuration Schema and Default Values

Date: 2026-03-18

## System Config Keys

- `recognition.threshold`: `0.8`
- `attendance.min_time_minutes`: `480`
- `attendance.windows`: JSON object (org-defined)
- `retention.days`: `35`
- `camera.stream.sampling_fps`: `1`
- `camera.wall.min_face_area_ratio`: `0.5`
- `enrollment.images.min_count`: `3`
- `enrollment.images.max_count`: `5`
- `quality.min_image_width`: `720`
- `quality.min_image_height`: `720`
- `quality.min_face_width_px`: `112`
- `quality.min_face_height_px`: `112`
- `quality.min_laplacian_variance`: `80.0`
- `quality.max_yaw_degrees`: `25`
- `quality.max_pitch_degrees`: `25`

## Attendance Status Mapping (Default)

- `present`: total_minutes >= min_time_minutes and valid in-window entry
- `partial`: total_minutes > 0 and total_minutes < min_time_minutes
- `absent`: no valid entry event in configured attendance window
- `late`: first entry exists but after allowed late threshold

## Notes

- All keys are dynamic and DB-driven.
- Admin can override defaults per organization.
- Changes must create audit log entries.
