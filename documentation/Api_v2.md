# APIs for Communication

## 1. Authorization APIs (`/v1/auth`)

### 1.1 Login

* **Task:** Authorize users based on credentials
* **Authority:** `Anyone`
* **Method:** `POST`
* **Endpoint:** `/v1/auth/login`

**Request Body**

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
* **Method:** `POST`
* **Endpoint:** `/v1/admin/config-org`

---

### 2.2 Configure System & Camera Details

* **Authority:** `Admin`
* **Method:** `POST`
* **Endpoint:** `/v1/admin/system-config`

---

### 2.3 System Health Check

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/system-health`

---

### 2.4 Add Operator

* **Authority:** `Admin`
* **Method:** `POST`
* **Endpoint:** `/v1/admin/add-operator`

---

### 2.5 Update Operator Details

* **Authority:** `Admin`
* **Method:** `PATCH`
* **Endpoint:** `/v1/admin/update-operator/{id}`

---

### 2.6 View Operator Details

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/view-operator/{id}`

---

### 2.7 Delete Operator

* **Authority:** `Admin`
* **Method:** `DELETE`
* **Endpoint:** `/v1/admin/delete-operator/{id}`

---

### 2.8 Get Operators List

* **Authority:** `Admin`
* **Method:** `GET`
* **Endpoint:** `/v1/admin/get-operators`

---

## 3. Operations APIs (`/v1/ops`)

> Accessible by **Admin** and **Operator** roles

---

### 3.1 Add User

* **Authority:** `Admin`, `Operator`
* **Method:** `POST`
* **Endpoint:** `/v1/ops/add-user`

---

### 3.2 Get Users List

* **Authority:** `Admin`, `Operator`
* **Method:** `GET`
* **Endpoint:** `/v1/ops/get-users`

---

### 3.3 Update User

* **Authority:** `Admin`, `Operator`
* **Method:** `PATCH`
* **Endpoint:** `/v1/ops/update-user/{id}`

---

### 3.4 Delete User

* **Authority:** `Admin`, `Operator`
* **Method:** `DELETE`
* **Endpoint:** `/v1/ops/delete-user/{id}`

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

---

### 3.7 Mark Manual Attendance

* **Authority:** `Admin`, `Operator`
* **Method:** `POST`
* **Endpoint:** `/v1/ops/mark-attendance`

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