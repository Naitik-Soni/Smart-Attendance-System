# APIs for Communication

## 1. Authorization APIs (`/v1/auth`)

### 1.1 Login

* **Task:** Authorize users based on credentials
* **Authority:** `Anyone`
* **Method:** `POST`
* **Endpoint:** `/v1/auth/login`

**Request body**

```json
{
  "user_id": "<unique id of the user>",
  "password": "<password assigned to the user>"
}
```

---

## 2. Admin APIs (`/v1/admin`)

### 2.1 Configure Organization Details

* **Authority:** `Admin`
* **Method:** `POST` or `PATCH`
* **Endpoint:** `/v1/admin/config-org`

**Request body:**
```json
{
  "org": {
    "org_name": "Acme Corp",
    "legal_name": "Acme Corp pvt. ltd.",
    "type": "enterprise"
  },

  "security": {
    "session_timeout_minutes": 30
  },

  "face_registration": {
    "max_faces_per_user": 5,
    "min_faces_per_user": 3,
    "min_image_quality_score": 0.75,
    "false_negative_priority": true
  },

  "data_policy": {
    "face_data_retention_days": 90,
    "log_retention_days": 180
  },

  "limits": {
    "api_rate_limit_per_min": 1000
  }
}
```

---

### 2.2 Configure System & Camera Details

* **Authority:** `Admin`
* **Method:** `POST` or `PATCH`
* **Endpoint:** `/v1/admin/system-config`

**Request body:**
```json
{
  "cameras": {
    "top_mounted": {
      "enabled": true,
      "devices": [
        {
          "enabled": true,
          "camera_id": "cam_001",
          "location": "headquarters",
          "input": {
            "type": "ip",
            "source": "192.168.14.56"
          }
        }
      ]
    },

    "wall_mounted": {
      "enabled": true,
      "devices": [
        {
          "enabled": true,
          "camera_id": "cam_wall_001",
          "location": "headquarters",
          "input": {
            "type": "rtsp",
            "source": "rtsp://admin:password@192.168.1.100:554/live"
          },
          "face_to_image_ratio": 0.5
        }
      ]
    }
  },

  "image_upload": {
    "enabled": true,
    "max_size_mb": 5,
    "min_quality_score": 0.75
  }
}
```

---

### 2.3 System Health Check

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/system-health`

---

### 2.4 Add Operator

* **Authority:** `Admin`
* **Method:** `POST`
* **Endpoint:** `/v1/admin/operator`

**Request body:**
```json
{
  "operator_id": "op1",
  "name": "John Doe",
  "email": "johndoe@xyz.in",
  "role": "operator",
  "status": "active"
}
```

---

### 2.5 Update Operator Details

* **Authority:** `Admin`
* **Method:** `PATCH`
* **Endpoint:** `/v1/admin/operator/{id}`

**Request body:**
```json
{
  "name": "John D",
  "status": "inactive"
}
```

---

### 2.6 View Operator Details

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/operator/{id}`

---

### 2.7 Delete Operator

* **Authority:** `Admin`
* **Method:** `DELETE`
* **Endpoint:** `/v1/admin/operator/{id}`

---

### 2.8 Get Operators List

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/operators`

## 3. Operations APIs (`/v1/ops`)

> Accessible by **Admin** and **Operator** roles

---

### 3.1 Add User

* **Authority:** `Admin`, `Operator`
* **Method:** `POST`
* **Endpoint:** `/v1/ops/user`

**Request body:**
```json
{
  "user_id": "u123",
  "name": "Jane Doe",
  "email": "jane@xyz.in",
  "role": "user",
  "status": "active"
}
```

---

### 3.2 Get Users List

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/users`

---

### 3.3 Update User

* **Authority:** `Admin`, `Operator`
* **Method:** `PATCH`
* **Endpoint:** `/v1/ops/user/{id}`

**Request body:**
```json
{
  "name": "John D",
  "status": "inactive"
}
```

---

### 3.4 Delete User

* **Authority:** `Admin`, `Operator`
* **Method:** `DELETE`
* **Endpoint:** `/v1/ops/user/{id}`

---

### 3.5 Get User Details

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/get-user/{id}`

---

### 3.6 Upload Image for Attendance Processing

* **Authority:** `Admin`, `Operator`
* **Method:** `POST`
* **Endpoint:** `/v1/ops/upload-image`
* **Content-Type:** `multipart/form-data`

**Request body:**
```json
{
    "image": FileUpload()
}
```

---

### 3.7 Mark Manual Attendance

* **Authority:** `Admin`, `Operator`
* **Method:** `POST`
* **Endpoint:** `/v1/ops/manual_attendance`

**Request body:**

```json
[
    {
        "user_id": "u123",
        "attendance_type": "manual",
        "status": "present",
        "timestamp": "2026-02-04T09:15:00Z",
        "reason": "Camera unavailable"
    }
]
```

---

### 3.8 Get Audit Logs

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/get-logs`

---

## 4. User APIs (`/v1/user`)

### 4.1 View Personal Attendance

* **Authority:** `User`
* **Method:** `GET`
* **Endpoint:** `/v1/user/get-attendance`