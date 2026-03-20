# Face API Contract (Aligned with Current Requirements)

Base path: `/faces`

## 1. Face Registration

### `POST /faces/register`
Form data:
- `user_id`
- `images[]` (required, 3-5)

Mandatory validations:
- exactly one face per enrollment image
- image quality gate pass

Response fragment:
```json
{
  "source": "enrollment",
  "face_registered": true,
  "user_id": "EMP_001"
}
```

## 2. Face Recognition

### `POST /faces/recognize`
Input:
```json
{
  "source_type": "wall_camera",
  "source_id": "ENTRY_GATE_1",
  "timestamp": "2026-03-18T10:22:00Z",
  "image": "base64_image"
}
```

Policy rules:
- default threshold is `> 0.8` (configurable)
- wall camera requires face area ratio > 0.5
- stream sampling happens upstream at 1 FPS

Response (multi-face):
```json
{
  "source_type": "wall_camera",
  "results": [
    {
      "face_index": 0,
      "status": "matched",
      "user_id": "EMP_001",
      "confidence": 0.84,
      "action": "entry_marked"
    },
    {
      "face_index": 1,
      "status": "unknown",
      "unknown_id": "unk_432"
    }
  ],
  "errors": []
}
```

Unknown or below-threshold outcomes:
- never auto-mark attendance
- persist traceability artifacts per policy

## 3. Delete Face

### `DELETE /faces/{face_id}`
Removes face registration mapping and associated embedding references.

## 4. Error Codes

- `NO_FACE_DETECTED`
- `MULTIPLE_FACES_IN_ENROLLMENT`
- `IMAGE_QUALITY_TOO_LOW`
- `INVALID_IMAGE`
- `MATCH_BELOW_THRESHOLD`
- `WALL_FACE_RATIO_TOO_LOW`
- `FACE_NOT_FOUND`

## Final Route Set

- `POST /faces/register`
- `POST /faces/recognize`
- `DELETE /faces/{face_id}`
