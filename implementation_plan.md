# Smart Attendance System — Implementation Plan

> [!IMPORTANT]
> **Constraints**: No Redis. Keep it simple — no caching, no background workers.
> **Priority**: Main API → Face API → DB design → HLD → Storage → Events → Backend API LLD
> **Face ingestion**: 3–5 images per user → 3–5 FAISS embeddings per user.

Two separate FastAPI services built from clean slate:
1. **`main_app/`** — Backend API (auth, users, attendance, admin, image upload)
2. **`face_service/`** — ML microservice (detect → align → embed → FAISS match)

---

## Proposed Changes

### main_app / Core

#### [NEW] `app/core/config.py`
`Settings` via pydantic-settings: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `FACE_SERVICE_URL`, `CORS_ORIGINS`, `STORAGE_ROOT`.

#### [NEW] `app/core/database.py`
SQLAlchemy `create_engine`, `sessionmaker`, `Base`, `get_db` dependency.

#### [NEW] `app/core/security.py`
JWT create/verify (`python-jose`), `hash_password` / `verify_password` (`passlib[bcrypt]`).

#### [NEW] `app/core/dependencies.py`
`get_db`, `get_current_user`, `require_admin`, `require_operator` FastAPI deps.

#### [NEW] `app/core/responses.py`
Standard response envelope: `{success, code, message, data, meta, errors}`.

#### [NEW] `app/core/exceptions.py`
`AppException` + global exception handler for clean JSON errors.

---

### main_app / Models (DB Design Priority)

#### [NEW] `app/models/organization.py`
`Organization`, `SystemConfig`, `ApplicationSettings`

#### [NEW] `app/models/user.py`
`Role` (seed: 1=ADMIN, 2=OPERATOR, 3=USER), `User`, `UserProfile` (with `faiss_user_id`)

#### [NEW] `app/models/attendance.py`
`AttendanceRecord`, `AttendanceLog`

#### [NEW] `app/models/face.py`
`FaceImage`, `FaceEmbedding`

#### [NEW] `app/models/audit.py`
`AuditLog`, `SystemLog`, `SystemHealth`

#### [NEW] `app/models/event.py`
`Event`, `Notification`

#### [MODIFY] [app/models/__init__.py](file:///C:/Users/baps/Documents/Projects/Smart-Attendance-System/main_app/app/models/__init__.py)
Re-export all models so Alembic sees `Base.metadata`.

---

### main_app / Schemas

#### [NEW] `app/schemas/auth.py` — `LoginRequest`, `TokenPair`, `UserInfo`
#### [NEW] `app/schemas/user.py` — `UserCreate`, `UserUpdate`, `UserOut`
#### [NEW] `app/schemas/admin.py` — `OrgConfigBody`, `SystemConfigBody`, `OperatorCreate`, `OperatorUpdate`, `OperatorOut`
#### [NEW] `app/schemas/ops.py` — `ManualAttendanceItem`, `AttendanceOut`, `AuditLogOut`, `ImageUploadResponse`

---

### main_app / Services

#### [NEW] `app/services/auth_service.py` — login, token generation
#### [NEW] `app/services/user_service.py` — user CRUD (soft-delete via `is_deleted`)
#### [NEW] `app/services/admin_service.py` — operator CRUD, org/system config upsert, health check
#### [NEW] `app/services/attendance_service.py` — mark manual attendance (bulk), get user records
#### [NEW] `app/services/face_client.py` — async `httpx` client → face_service
#### [NEW] `app/services/audit_service.py` — write + read audit logs

---

### main_app / Routers

#### [NEW] `app/api/v1/auth.py` — `POST /v1/auth/login`
#### [NEW] `app/api/v1/admin.py` — `POST/PATCH config-org`, `POST/PATCH system-config`, `GET system-health`, operator CRUD (5 endpoints)
#### [NEW] `app/api/v1/ops.py` — user CRUD (5 endpoints), `POST upload-image`, `POST manual_attendance`, `GET get-logs`
#### [NEW] `app/api/v1/user.py` — `GET /v1/user/get-attendance`
#### [MODIFY] [app/api/v1/__init__.py](file:///C:/Users/baps/Documents/Projects/Smart-Attendance-System/main_app/app/api/v1/__init__.py) — aggregate router
#### [MODIFY] [app/main.py](file:///C:/Users/baps/Documents/Projects/Smart-Attendance-System/main_app/app/main.py) — app factory, CORS, routers, exception handlers

#### [MODIFY] [alembic/env.py](file:///C:/Users/baps/Documents/Projects/Smart-Attendance-System/main_app/alembic/env.py) — import `Base` from `app.models`

---

### face_service / Core

#### [NEW] `app/core/config.py` — `MODEL_PATH`, `EMBEDDING_DIM=512`, `FAISS_INDEX_PATH`, `FAISS_ID_MAP_PATH`, `STORAGE_ROOT`, `CONFIDENCE_THRESHOLD`
#### [NEW] `app/core/exceptions.py` — structured face service errors

---

### face_service / Engine

#### [NEW] `app/engine/detector.py`
`FaceDetector` — OpenCV Haar Cascade. Rejects blurry (Laplacian) or too-small faces.

#### [NEW] `app/engine/aligner.py`
`FaceAligner` — crops + resizes to 112×112 (ArcFace standard).

#### [NEW] `app/engine/embedder.py`
`FaceEmbedder` — ArcFace ONNX inference. Falls back to random normalized vector in dev mode if model not present.

#### [NEW] `app/engine/matcher.py`
`FaceMatcher` — cosine similarity on `IndexFlatIP` FAISS index.

---

### face_service / Vector Store

#### [NEW] `app/vector/embedding_store.py`
`EmbeddingStore` — add / search / remove / save / load FAISS index.

#### [NEW] `app/vector/id_map.py`
`IDMap` — JSON file: `{faiss_int_id → {user_id, image_file}}`.

---

### face_service / Schemas + Services + API

#### [NEW] `app/schemas/face.py`
`RegisterRequest`, `RecognizeRequest`, `FaceResult`, `RecognizeResponse`, `RegisterResponse`

#### [NEW] `app/services/registration_service.py`
`register_faces(user_id, images[3-5])`: detect → align → embed → add to FAISS + id_map (3–5 embeddings).

#### [NEW] `app/services/recognition_service.py`
`recognize(source_type, source_id, timestamp, image)`: full pipeline → per-face result list.

#### [NEW] `app/api/v1/faces.py`
- `POST /faces/register` (form: `user_id`, `images[]` 3–5 files)
- `POST /faces/recognize` (JSON body)
- `DELETE /faces/{face_id}`

#### [MODIFY] [app/main.py](file:///C:/Users/baps/Documents/Projects/Smart-Attendance-System/main_app/app/main.py) — face_service app, startup loads FAISS index.

---

## Verification Plan

### Step 1 — Imports
```powershell
python -c "from app.main import app; print('OK')"
```
Run in both `main_app/` and `face_service/`.

### Step 2 — Start servers
```powershell
# face_service — port 8001
uvicorn app.main:app --port 8001 --reload

# main_app — port 8000
uvicorn app.main:app --port 8000 --reload
```

### Step 3 — Swagger smoke test
- `http://localhost:8000/docs` — all 14+ routes visible
- `http://localhost:8001/docs` — 3 face routes visible

### Step 4 — Auth + Operator round-trip
1. `POST /v1/auth/login` → get token
2. Use token → `POST /v1/admin/operator` → `OPERATOR_CREATED`

### Step 5 — Face registration
`POST /faces/register` with 3 test images → expect `face_registered: true`

> [!NOTE]
> **Before running migrations**, I'll tell you to install and configure **PostgreSQL** and **FAISS** (`faiss-cpu`).
