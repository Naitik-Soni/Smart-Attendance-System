# Migration Strategy (Pre-Coding)

Date: 2026-03-18

## Strategy Decision

Use incremental forward migrations from current schema state.
Do not reset production-like data.

## Steps

1. Baseline current live schema and migration head.
2. Generate migration set for new policy/config/storage tables and columns.
3. Add data backfill migration for default config keys.
4. Add safe indexes and unique constraints for attendance daily uniqueness.
5. Add rollback scripts for each migration step.
6. Run migrations in staging with realistic snapshot.
7. Promote to production with backup + verification checklist.

## Non-Negotiables

- No destructive migration without explicit backup/approval.
- Every migration must be reversible.
- Migration scripts must include data validation checks.

## Verification After Migration

- config reads/writes work for required keys
- attendance unique daily record constraint holds
- storage backend registry and references query correctly
- old APIs remain backward-compatible where required
