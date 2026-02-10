# 1️⃣ Profiles & Users (Postgres)

This is the **root** of almost everything else.

## Purpose

* Authentication & authorization
* Role-based access (Admin / Operator / User)
* Organization-level isolation (important for scale)

---

## Tables

### 1. `organizations`

```sql
CREATE TABLE organizations (
    id              UUID PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    legal_name       VARCHAR(255) NOT NULL,
    code            VARCHAR(50) UNIQUE NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,

    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Notes**

* `code` helps in URLs, configs, license checks
* Almost everything will FK to `organization_id`

---

### 2. `roles`

```sql
CREATE TABLE roles (
    id          SMALLINT PRIMARY KEY,
    role_name        VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);
```

**Seed data**

```text
1 → ADMIN
2 → OPERATOR
3 → USER
```

---

### 3. `users`

```sql
CREATE TABLE users (
    id                  UUID PRIMARY KEY,
    organization_id     UUID NOT NULL REFERENCES organizations(id),

    username            VARCHAR(100) UNIQUE NOT NULL,
    email               VARCHAR(255),
    password_hash       TEXT NOT NULL,

    role_id             SMALLINT NOT NULL REFERENCES roles(id),

    is_active           BOOLEAN DEFAULT TRUE,
    is_deleted          BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Indexes**

```sql
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_role ON users(role_id);
```

---

### 4. `user_profiles`

```sql
CREATE TABLE user_profiles (
    user_id         UUID PRIMARY KEY REFERENCES users(id),

    full_name       VARCHAR(255),
    employee_code   VARCHAR(100),
    department      VARCHAR(100),
    faiss_user_id   INTEGER UNIQUE NOT NULL

    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

**Why separate?**

* Keeps `users` lean
* Profile info changes more often than auth info

---

### Redis usage here ❌

Correct decision: **NO user data in Redis**

---

# 2️⃣ Attendance (Postgres + Redis for Today)

This is **core business data**.

---

## Tables

### 1. `attendance_records`

```sql
CREATE TABLE attendance_records (
    id              UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id         UUID NOT NULL REFERENCES users(id),

    attendance_date DATE NOT NULL,

    first_in_time   TIMESTAMP,
    last_out_time   TIMESTAMP,

    total_minutes   INTEGER,

    source          VARCHAR(50), -- CAMERA / MANUAL / API
    confidence      NUMERIC(5,2),

    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

**Indexes**

```sql
CREATE INDEX idx_attendance_user_date 
ON attendance_records(user_id, attendance_date);
```

---

### 2. `attendance_logs` (every in/out event)

```sql
CREATE TABLE attendance_logs (
    id              UUID PRIMARY KEY,
    attendance_id   UUID REFERENCES attendance_records(id),

    event_type      VARCHAR(10), -- IN / OUT
    event_time      TIMESTAMP NOT NULL,

    camera_id       UUID,
    confidence      NUMERIC(5,2),

    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## Redis (VERY GOOD USE CASE)

### Redis Keys

```text
attendance:today:{org_id}:{user_id}
```

### Redis Value (example)

```json
{
  "first_in": "2026-02-10T09:12:00",
  "last_out": "2026-02-10T18:01:00",
  "events": [
    {"type": "IN", "time": "..."},
    {"type": "OUT", "time": "..."}
  ]
}
```

**Flush to Postgres**

* At day end OR
* On Redis TTL expiry

---

# 3️⃣ Audit Logs (Postgres)

This is **write-heavy**, design carefully.

---

## Tables

### 1. `audit_logs`

```sql
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    organization_id UUID,
    user_id         UUID,

    action          VARCHAR(100),
    entity_type     VARCHAR(100),
    entity_id       VARCHAR(100),

    ip_address      INET,
    user_agent      TEXT,

    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

### 2. `system_logs`

```sql
CREATE TABLE system_logs (
    id              BIGSERIAL PRIMARY KEY,
    log_level       VARCHAR(20), -- INFO/WARN/ERROR
    service_name    VARCHAR(100),

    message         TEXT,
    metadata        JSONB,

    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

### 3. `system_health`

```sql
CREATE TABLE system_health (
    id              BIGSERIAL PRIMARY KEY,
    service_name    VARCHAR(100),
    status          VARCHAR(20), -- UP/DOWN/DEGRADED

    cpu_usage       NUMERIC(5,2),
    memory_usage    NUMERIC(5,2),

    recorded_at     TIMESTAMP DEFAULT NOW()
);
```

---

### Redis ❌

Nope. Logs grow too fast.

---

# 4️⃣ Storage (File System)

No DB tables for images themselves ❌
Only **metadata in Postgres**.

---

## Tables

### `face_images`

```sql
CREATE TABLE face_images (
    id              UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id         UUID REFERENCES users(id), -- NULL for unknown

    image_type      VARCHAR(20), -- KNOWN / UNKNOWN
    file_path       TEXT NOT NULL,

    captured_at     TIMESTAMP,
    camera_id       UUID,

    created_at      TIMESTAMP DEFAULT NOW()
);
```

**Rules**

* Max **3–5 images per user** (enforced in service, not DB)
* Unknown faces → `user_id = NULL`

---

# 5️⃣ Vector Storage (FAISS)

FAISS ≠ transactional DB → keep metadata in Postgres.

---

## Table

### `face_embeddings`

```sql
CREATE TABLE face_embeddings (
    id              UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id         UUID REFERENCES users(id),

    embedding_index INTEGER NOT NULL, -- FAISS index id
    image_id        UUID REFERENCES face_images(id),

    created_at      TIMESTAMP DEFAULT NOW()
);
```

**Why this table matters**

* Rebuild FAISS if corrupted
* Track which embedding belongs to which image

---

# 6️⃣ Organization & System Config (Postgres + Redis)

---

## Tables

### 1. `system_configs`

```sql
CREATE TABLE system_configs (
    id              UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),

    config_key      VARCHAR(100),
    config_value    JSONB,

    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),

    UNIQUE (organization_id, config_key)
);
```

---

### 2. `application_settings`

```sql
CREATE TABLE application_settings (
    id              UUID PRIMARY KEY,
    setting_key     VARCHAR(100) UNIQUE,
    setting_value   JSONB,

    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

## Redis (Correct usage)

### Keys

```text
config:system:{org_id}
config:app
```

TTL = Admin-configured

---

# 7️⃣ Events & Notifications (Postgres)

---

## Tables

### 1. `events`

```sql
CREATE TABLE events (
    id              UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),

    event_type      VARCHAR(50), -- UNKNOWN_FACE, LOW_CONFIDENCE
    severity        VARCHAR(20),

    reference_id    UUID, -- face_image_id, attendance_id
    metadata        JSONB,

    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

### 2. `notifications`

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY,
    event_id        UUID REFERENCES events(id),

    channel         VARCHAR(20), -- EMAIL / SMS / DASHBOARD
    status          VARCHAR(20), -- SENT / FAILED / PENDING

    created_at      TIMESTAMP DEFAULT NOW()
);
```