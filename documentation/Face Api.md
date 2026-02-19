# 1️⃣ Face Registration

### `POST /faces/register`

```
Form Data:
- user_id
- images[] (3–5)
```

### Response

```json
{
  "face_id": "face_001",
  "user_id": "EMP_001",
  "face_registered": "true"
}
```

---

# 2️⃣ Face Detection / Recognition (Source Aware)

### `POST /faces/recognize`

### Input

```json
{
  "source_type": "wall_camera",
  "source_id": "ENTRY_GATE_1",
  "timestamp": "2026-02-19T10:22:00",
  "image": "base64_or_file"
}
```

---

# Internal Behavior Based on Source

### wall_camera

* Frontal faces
* Standard threshold (e.g., 0.75)

### ceiling_camera

* Top angle
* Lower threshold (e.g., 0.65)
* Possibly stricter face size filtering

### upload_image

* Manual verification mode
* Higher threshold (e.g., 0.70)
* No attendance marking

---

# Response (Multi-Face)

```json
{
  "source_type": "wall_camera",
  "results": [
    {
      "face_index": 0,
      "status": "matched",
      "face_id": "face_001",
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

If upload image:

```json
{
  "source_type": "upload_image",
  "results": [
    {
      "face_index": 0,
      "status": "matched",
      "face_id": "face_001",
      "confidence": 0.91,
      "action": "verification_only"
    }
  ],
  "errors": []
}
```

---

# 3️⃣ Delete Face

### `DELETE /faces/{face_id}`

```json
{
  "status": "deleted",
  "face_id": "face_001"
}
```

---

# Final Clean Structure

```
POST   /faces/register
POST   /faces/recognize   (source-aware)
DELETE /faces/{face_id}
```