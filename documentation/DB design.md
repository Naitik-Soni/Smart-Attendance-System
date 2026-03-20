# Database Design (Doc Source of Truth)

## Scope

This design supports:
- identity and organization isolation,
- recognition + attendance workflows,
- dynamic policy configuration,
- pluggable storage backend metadata,
- 35-day retention operations.

## 1. Identity and Organization

### `organizations`
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### `roles`
```sql
CREATE TABLE roles (
    id SMALLINT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);
```

Seed values:
- 1 = ADMIN
- 2 = OPERATOR
- 3 = USER

### `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash TEXT NOT NULL,
    role_id SMALLINT NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### `user_profiles`
```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    full_name VARCHAR(255),
    employee_code VARCHAR(100),
    department VARCHAR(100),
    faiss_user_id INTEGER UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 2. Attendance

### `attendance_records`
```sql
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    attendance_date DATE NOT NULL,
    first_in_time TIMESTAMP,
    last_out_time TIMESTAMP,
    total_minutes INTEGER,
    attendance_status VARCHAR(20),
    source VARCHAR(50),
    confidence NUMERIC(5,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (organization_id, user_id, attendance_date)
);
```

### `attendance_logs`
```sql
CREATE TABLE attendance_logs (
    id UUID PRIMARY KEY,
    attendance_id UUID NOT NULL REFERENCES attendance_records(id),
    event_type VARCHAR(10) NOT NULL, -- ENTRY / EXIT
    event_time TIMESTAMP NOT NULL,
    camera_id VARCHAR(100),
    source_type VARCHAR(50),
    confidence NUMERIC(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);
```

Rule mapping:
- Store all entry/exit events in `attendance_logs`.
- `attendance_records.total_minutes = last_out_time - first_in_time`.
- `MIN_TIME` and windows determine `attendance_status`.

## 3. Face Image and Embedding Metadata

### `face_images`
```sql
CREATE TABLE face_images (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID REFERENCES users(id), -- NULL for unknown
    image_type VARCHAR(20) NOT NULL, -- KNOWN / UNKNOWN / ENROLLMENT
    file_path TEXT NOT NULL,
    storage_backend_key VARCHAR(100),
    captured_at TIMESTAMP,
    camera_id VARCHAR(100),
    source_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `face_embeddings`
```sql
CREATE TABLE face_embeddings (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    embedding_index INTEGER NOT NULL,
    image_id UUID REFERENCES face_images(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 4. Audit and Ops Logs

### `audit_logs`
```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID,
    user_id UUID,
    action VARCHAR(100),
    entity_type VARCHAR(100),
    entity_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `system_logs`
```sql
CREATE TABLE system_logs (
    id BIGSERIAL PRIMARY KEY,
    log_level VARCHAR(20),
    service_name VARCHAR(100),
    message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 5. Dynamic Policy and Configuration

### `system_configs`
```sql
CREATE TABLE system_configs (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (organization_id, config_key)
);
```

Expected `config_key` examples:
- `recognition.threshold` (default `0.8`, rule is match `> threshold`)
- `attendance.min_time_minutes`
- `attendance.windows`
- `retention.days` (default `35`)
- `camera.wall.min_face_area_ratio` (default `0.5`)
- `camera.stream.sampling_fps` (default `1`)

### `application_settings`
```sql
CREATE TABLE application_settings (
    id UUID PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 6. Pluggable Storage Backend Registry

### `storage_backends`
```sql
CREATE TABLE storage_backends (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    backend_key VARCHAR(100) NOT NULL,      -- local_fs / s3 / minio / gcs
    backend_type VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (organization_id, backend_key)
);
```

### `storage_artifacts` (optional but recommended)
```sql
CREATE TABLE storage_artifacts (
    id UUID PRIMARY KEY,
    backend_id UUID NOT NULL REFERENCES storage_backends(id),
    artifact_type VARCHAR(50) NOT NULL,     -- face_image / model / export
    artifact_ref VARCHAR(255) NOT NULL,
    checksum VARCHAR(128),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 7. Retention Policy Support

Retention rule (current):
- Keep recognition-related operational data for up to 35 days.

Data classes covered by retention cleanup:
- unknown face images metadata,
- transient recognition logs,
- policy-defined deletable operational artifacts.

Suggested implementation:
- Scheduled purge job using `retention.days` from `system_configs`.
- Purge should delete both DB metadata and storage objects through storage plugin interface.
