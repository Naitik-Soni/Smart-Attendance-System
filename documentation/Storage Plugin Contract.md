# Storage Plugin Contract

Date: 2026-03-18

## Interface Methods (Required)

- `save_image(bytes, path_hint, metadata) -> artifact_ref`
- `read_image(artifact_ref) -> bytes`
- `delete_image(artifact_ref) -> bool`
- `exists(artifact_ref) -> bool`
- `get_signed_url(artifact_ref, expires_in) -> url` (optional for private backends)
- `health_check() -> {status, details}`

## Behavior Rules

- All image read/write/delete must go through this interface.
- Plugins must be backend-agnostic to business logic.
- Plugin operations must emit structured error codes.
- Plugin failure should not crash core API process.

## Standard Error Codes

- `STORAGE_BACKEND_UNAVAILABLE`
- `STORAGE_WRITE_FAILED`
- `STORAGE_READ_FAILED`
- `STORAGE_DELETE_FAILED`
- `STORAGE_INVALID_REFERENCE`

## Backend Registry Rules

- Multiple backends can be configured.
- Exactly one backend should be default active backend per organization.
- Disabled backend cannot accept new writes.
