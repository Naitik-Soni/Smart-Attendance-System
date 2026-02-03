# 📦 Storage System – Low Level Design (LLD)

## 🔒 Design Goals (non-negotiable)

* Prefer **false negatives over false positives**
* Storage must be **replaceable** (no hard coupling)
* Windows-friendly
* Works **without UI**
* Scales from single machine → distributed later

---

## 🧱 Final Storage Stack (Frozen)

| Data Type          | Storage                      |
| ------------------ | ---------------------------- |
| User & Access Data | **PostgreSQL**               |
| Face Images        | **Filesystem (NTFS)**        |
| Face Embeddings    | **FAISS**                    |
| Logs & Events      | **PostgreSQL (append-only)** |
| System Health      | **Redis**                    |

---

## 🗂️ 1️⃣ Filesystem LLD – Face Images

### 📁 Root Layout

```
/storage/
 └── images/
     ├── users/
     └── unknown/
```

---

### 👤 Known Users

```
/storage/images/users/{user_id}/
 ├── original/
 │    ├── img_001.jpg
 │    └── img_002.jpg
 ├── aligned/
 │    ├── face_001.png
 │    └── face_002.png
 └── metadata.json
```

**Rules**

* `original/` → never deleted
* `aligned/` → only model-ready faces
* `metadata.json`:

```json
{
  "created_at": "...",
  "camera_id": "...",
  "quality_score": 0.87
}
```

---

### ❓ Unknown Faces

```
/storage/images/unknown/{date}/
 ├── cam_01_1700.png
 ├── cam_02_1822.png
```

**Retention**

* Auto-delete after **N days**
* Used only for review / future learning

---

## 🧠 2️⃣ FAISS LLD – Face Embeddings (CORE)

### 📌 Index Design

* Index type: `IndexFlatIP` (cosine similarity)
* Embedding size: **512**
* Normalized vectors ONLY

```
/storage/embeddings/
 ├── faiss.index
 ├── id_map.json
 └── stats.json
```

---

### 🧩 ID Mapping (CRITICAL)

```json
{
  "0": { "user_id": "U123", "image": "face_001.png" },
  "1": { "user_id": "U123", "image": "face_002.png" },
  "2": { "user_id": "U456", "image": "face_003.png" }
}
```

> FAISS knows only numbers — **YOU** maintain meaning.

---

### 🧠 Embedding Lifecycle (Frozen Logic)

| Case                         | Action                     |
| ---------------------------- | -------------------------- |
| New user                     | Add ≥ 3 embeddings         |
| Recognized (high confidence) | Optionally add embedding   |
| Low confidence               | ❌ DO NOT add               |
| False positive risk          | Block auto-learning        |
| User deleted                 | Remove IDs + rebuild index |

⚠️ **No auto-learning unless confidence > threshold**

---

## 🗄️ 3️⃣ PostgreSQL LLD – Core Tables

### 👤 `users`

```sql
id (PK)
name
department
status (active/disabled)
created_at
```

---

### 🔐 `roles`

```sql
id
role_name
```

---

### 🧾 `recognition_events` (append-only)

```sql
id
timestamp
camera_id
matched_user_id (nullable)
confidence
is_unknown
```

---

### 📷 `camera_events`

```sql
id
camera_id
event_type
timestamp
details
```

**Rules**

* ❌ No UPDATE
* ❌ No DELETE
* ✔ Audit safe

---

## ⚡ 4️⃣ Redis LLD – System Health

### 🔑 Key Design

```
camera:{id}:last_seen → timestamp (TTL)
camera:{id}:status → online/offline
worker:{id}:heartbeat → timestamp
queue:recognition:size → int
```

**TTL Strategy**

* If key expires → component assumed dead

---

## 🔁 5️⃣ Storage Access Layer (VERY IMPORTANT)

### ❌ Forbidden

* Direct DB calls from API
* Direct FAISS calls from API

### ✅ Required

```
/storage/
 ├── image_store.py
 ├── embedding_store.py
 ├── db_store.py
 └── cache_store.py
```

Each exposes **interfaces**, not implementations.

Example reminder:

```python
embedding_store.search(vector) → matches
```

---

## 🧠 Failure Handling (LLD Level)

| Failure         | Handling                    |
| --------------- | --------------------------- |
| Corrupted image | Log + skip                  |
| FAISS crash     | Reload from disk            |
| Redis down      | System continues (degraded) |
| DB down         | Read-only mode              |
| Camera silent   | TTL expiry → offline        |

---

## 🏁 FINAL STORAGE FLOW (Authoritative)


```
Camera → Image Store
       → Face Model
       → Embedding Store (FAISS)
       → Match Decision
       → Event Log (Postgres)
       → Health Update (Redis)
```
