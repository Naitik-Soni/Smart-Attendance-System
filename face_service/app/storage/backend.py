from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings
from app.core.exceptions import FaceException


class LocalImageStorage:
    def __init__(self, root: str):
        self.root = Path(root)

    def save_image(self, image: np.ndarray, relative_path: str) -> str:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(path), image):
            raise FaceException(500, "STORAGE_WRITE_FAILED", f"Failed to store image '{relative_path}'")
        return str(path)

    def exists(self, relative_path: str) -> bool:
        return (self.root / relative_path).exists()

    def delete(self, relative_path: str) -> bool:
        path = self.root / relative_path
        if not path.exists():
            return False
        path.unlink()
        return True

    def health_check(self) -> dict:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            return {"status": "healthy", "backend": "local_fs", "root": str(self.root)}
        except Exception as exc:
            return {"status": "unhealthy", "backend": "local_fs", "error": str(exc)}


_backend = LocalImageStorage(settings.STORAGE_ROOT)


def get_storage_backend() -> LocalImageStorage:
    return _backend
