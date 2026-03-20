# Retention Scope and Data Lifecycle

Date: 2026-03-18
Default policy: 35 days

## Purge After 35 Days

- unknown face images metadata and files
- transient recognition artifacts
- temporary preprocessing artifacts
- non-essential operational face-capture traces

## Keep Longer (Not Auto-Purged by 35-day rule)

- attendance summary and attendance logs (business records)
- audit logs (security/compliance records)
- user and organization identity records
- policy configuration change history

## Purge Requirements

- Purge must run through storage plugin interface.
- Purge action must be auditable.
- Purge operation must be idempotent and retry-safe.
