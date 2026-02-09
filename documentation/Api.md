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
**Sample Response (Success)**
```json
{
  "success": true,
  "code": "LOGIN_SUCCESS",
  "message": "Login successful",
  "data": {
    "user": {
      "user_id": "admin_01",
      "role": "admin",
      "name": "Admin User"
    },
    "tokens": {
      "access_token": "jwt_access_token",
      "refresh_token": "jwt_refresh_token",
      "expires_in": 1800
    }
  },
  "meta": {},
  "errors": []
}
```

**Sample Response (Invalid credentials)**
```
{
  "success": false,
  "code": "INVALID_CREDENTIALS",
  "message": "Invalid user ID or password",
  "data": null,
  "meta": {},
  "errors": []
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
**Sample Response:**
```json
{
  "success": true,
  "code": "CONFIG_UPDATED",
  "message": "Configuration saved successfully",
  "data": {
    "version": "v2",
    "updated_at": "2026-02-04T10:30:00Z"
  },
  "meta": {},
  "errors": []
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

**Sample Response:**
```json
{
  "success": true,
  "code": "CONFIG_UPDATED",
  "message": "Configuration saved successfully",
  "data": {
    "version": "v3",
    "updated_at": "2026-02-04T10:30:00Z"
  },
  "meta": {},
  "errors": []
}
```

---

### 2.3 System Health Check

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/system-health`

**Sample Response:**
```json
{
  "success": true,
  "code": "SYSTEM_HEALTH_OK",
  "message": "System is healthy",
  "data": {
    "services": {
      "api": "healthy",
      "db": "healthy",
      "face_engine": "healthy",
      "storage": "healthy"
    },
    "uptime_seconds": 345678
  },
  "meta": {
    "checked_at": "2026-02-04T11:00:00Z"
  },
  "errors": []
}
```


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

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATOR_CREATED",
  "message": "Operator added successfully",
  "data": {
    "operator_id": "op1"
  },
  "meta": {},
  "errors": []
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

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATOR_UPDATED",
  "message": "Operator details updated",
  "data": {
    "operator_id": "op1"
  },
  "meta": {},
  "errors": []
}
```

---

### 2.6 View Operator Details

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/operator/{id}`

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATOR_FETCHED",
  "message": "Operator details retrieved",
  "data": {
    "operator_id": "op1",
    "name": "John Doe",
    "email": "johndoe@xyz.in",
    "status": "active"
  },
  "meta": {},
  "errors": []
}
```

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATOR_FETCHED",
  "message": "Operator details retrieved",
  "data": {
    "operator_id": "op1",
    "name": "John Doe",
    "email": "johndoe@xyz.in",
    "status": "active"
  },
  "meta": {},
  "errors": []
}
```

---

### 2.7 Delete Operator

* **Authority:** `Admin`
* **Method:** `DELETE`
* **Endpoint:** `/v1/admin/operator/{id}`

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATOR_DELETED",
  "message": "Operator deleted successfully",
  "data": null,
  "meta": {},
  "errors": []
}
```


---

### 2.8 Get Operators List

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/operators`

**Sample Response:**
```json
{
  "success": true,
  "code": "OPERATORS_LIST",
  "message": "Operators fetched successfully",
  "data": [
    {
      "operator_id": "op1",
      "name": "John Doe",
      "status": "active"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "page_size": 20
  },
  "errors": []
}
```


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

**Sample Response:**
```json
{
  "success": true,
  "code": "USER_CREATED",
  "message": "User added successfully",
  "data": {
    "user_id": "u123"
  },
  "meta": {},
  "errors": []
}
```

---

### 3.2 Get Users List

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/users`

**Sample Response:**
```json
{
  "success": true,
  "code": "USERS_LIST",
  "message": "Users fetched successfully",
  "data": [
    {
      "user_id": "u123",
      "name": "Jane Doe",
      "status": "active"
    }
  ],
  "meta": {
    "total": 45,
    "page": 1,
    "page_size": 20
  },
  "errors": []
}
```

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

**Sample Response:**
```json
{
  "success": true,
  "code": "USER_FETCHED",
  "message": "User details retrieved",
  "data": {
    "user_id": "u123",
    "name": "Jane Doe",
    "email": "jane@xyz.in",
    "status": "active"
  },
  "meta": {},
  "errors": []
}
```

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

**Sample Response:**
```json
{
  "success": true,
  "code": "IMAGE_RECEIVED",
  "message": "Image uploaded successfully, processing started",
  "data": {
    "request_id": "img_req_98765",
    "status": "processing"
  },
  "meta": {},
  "errors": []
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

**Sample Response:**
```json
{
  "success": true,
  "code": "ATTENDANCE_MARKED",
  "message": "Attendance marked successfully",
  "data": {
    "processed": 1,
    "failed": 0
  },
  "meta": {
    "request_type": "bulk"
  },
  "errors": []
}
```

---

### 3.8 Get Audit Logs

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/get-logs`

**Sample Response:**
```json
{
  "success": true,
  "code": "LOGS_FETCHED",
  "message": "Audit logs retrieved",
  "data": [
    {
      "action": "USER_CREATED",
      "actor": "admin",
      "timestamp": "2026-02-04T09:10:00Z"
    }
  ],
  "meta": {
    "total": 120
  },
  "errors": []
}
```

---

## 4. User APIs (`/v1/user`)

### 4.1 View Personal Attendance

* **Authority:** `User`
* **Method:** `GET`
* **Endpoint:** `/v1/user/get-attendance`

**Sample Response:**
```json
{
  "success": true,
  "code": "ATTENDANCE_FETCHED",
  "message": "Attendance records retrieved",
  "data": [
    {
      "date": "2026-02-04",
      "status": "present",
      "method": "face"
    }
  ],
  "meta": {},
  "errors": []
}
```