from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings


def purge_unknown_images(retention_days: int | None = None) -> dict:
    keep_days = int(retention_days or settings.RETENTION_DAYS)
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=keep_days)).date()
    unknown_root = Path(settings.STORAGE_ROOT) / "images" / "unknown"

    if not unknown_root.exists():
        return {"deleted_files": 0, "deleted_dirs": 0, "retention_days": keep_days}

    deleted_files = 0
    deleted_dirs = 0

    for day_dir in unknown_root.iterdir():
        if not day_dir.is_dir():
            continue
        try:
            dir_date = datetime.strptime(day_dir.name, "%Y-%m-%d").date()
        except ValueError:
            continue

        if dir_date > cutoff_date:
            continue

        for p in day_dir.rglob("*"):
            if p.is_file():
                p.unlink(missing_ok=True)
                deleted_files += 1

        # Remove empty folders bottom-up.
        for p in sorted(day_dir.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass

        try:
            day_dir.rmdir()
            deleted_dirs += 1
        except OSError:
            pass

    return {"deleted_files": deleted_files, "deleted_dirs": deleted_dirs, "retention_days": keep_days}
