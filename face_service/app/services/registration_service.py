from pathlib import Path

import cv2
import numpy as np
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FaceException
from app.engine.aligner import aligner
from app.engine.detector import detector
from app.engine.embedder import embedder
from app.storage import get_storage_backend
from app.vector.embedding_store import EmbeddingStore
from app.vector.id_map import IDMapStore


def _decode_upload(upload: UploadFile) -> np.ndarray:
    raw = upload.file.read()
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise FaceException(400, "INVALID_IMAGE", f"Could not decode image '{upload.filename}'")
    return img


def _save_image(image: np.ndarray, path: Path) -> None:
    storage = get_storage_backend()
    relative_path = str(path).replace("\\", "/")
    if relative_path.startswith("./"):
        relative_path = relative_path[2:]
    marker = "/images/"
    if marker in relative_path:
        relative_path = relative_path.split(marker, 1)[1]
        relative_path = f"images/{relative_path}"
    storage.save_image(image, relative_path)


def _policy_int(policies: dict | None, key: str, fallback: int) -> int:
    if not policies or key not in policies:
        return int(fallback)
    try:
        return int(policies[key])
    except Exception:
        return int(fallback)


def _policy_float(policies: dict | None, key: str, fallback: float) -> float:
    if not policies or key not in policies:
        return float(fallback)
    try:
        return float(policies[key])
    except Exception:
        return float(fallback)


def _validate_image_quality(img: np.ndarray, filename: str | None, policies: dict | None) -> None:
    h, w = img.shape[:2]
    min_w = _policy_int(policies, "quality.min_image_width", settings.QUALITY_MIN_IMAGE_WIDTH)
    min_h = _policy_int(policies, "quality.min_image_height", settings.QUALITY_MIN_IMAGE_HEIGHT)
    if w < min_w or h < min_h:
        raise FaceException(
            400,
            "IMAGE_QUALITY_TOO_LOW",
            (
                f"Image '{filename or 'unknown'}' resolution too low: "
                f"{w}x{h}, minimum {min_w}x{min_h}"
            ),
        )


def _select_single_face(faces: list[dict], filename: str | None, policies: dict | None) -> dict:
    if not faces:
        raise FaceException(400, "NO_FACE_DETECTED", f"No face detected in '{filename}'")
    if len(faces) > 1:
        raise FaceException(
            400,
            "MULTIPLE_FACES_IN_ENROLLMENT",
            f"Enrollment image '{filename}' must contain exactly one face",
        )

    only_face = faces[0]
    x1, y1, x2, y2 = only_face["box"]
    width = x2 - x1
    height = y2 - y1
    min_w = _policy_int(policies, "quality.min_face_width_px", settings.QUALITY_MIN_FACE_WIDTH_PX)
    min_h = _policy_int(policies, "quality.min_face_height_px", settings.QUALITY_MIN_FACE_HEIGHT_PX)
    if width < min_w or height < min_h:
        raise FaceException(
            400,
            "IMAGE_QUALITY_TOO_LOW",
            (
                f"Face in '{filename}' is too small: {width}x{height}, "
                f"minimum {min_w}x{min_h}"
            ),
        )
    return only_face


def register_faces(
    user_id: str,
    images: list[UploadFile],
    store: EmbeddingStore,
    id_map: IDMapStore,
    policies: dict | None = None,
) -> dict:
    min_images = _policy_int(policies, "enrollment.images.min_count", 3)
    max_images = _policy_int(policies, "enrollment.images.max_count", 5)
    if not min_images <= len(images) <= max_images:
        raise FaceException(400, "INVALID_IMAGE_COUNT", f"Provide {min_images} to {max_images} images")

    face_id = f"face_{user_id}"
    vectors = []
    payloads = []
    user_root = Path(settings.STORAGE_ROOT) / "images" / "users" / user_id
    original_dir = user_root / "original"
    aligned_dir = user_root / "aligned"

    for i, upload in enumerate(images):
        img = _decode_upload(upload)
        _validate_image_quality(img, upload.filename, policies)
        _save_image(img, original_dir / f"img_{i+1:03d}.jpg")

        blur_threshold = _policy_float(policies, "quality.min_laplacian_variance", settings.QUALITY_MIN_LAPLACIAN_VARIANCE)
        faces = detector.detect(img, min_laplacian_variance=blur_threshold)
        best = _select_single_face(faces, upload.filename, policies)
        aligned = aligner.align(img, best["box"], best.get("landmarks"))
        aligned_file = aligned_dir / f"face_{i+1:03d}.png"
        _save_image(aligned, aligned_file)

        emb = embedder.embed(aligned)
        vectors.append(emb)
        payloads.append(
            {
                "user_id": user_id,
                "face_id": face_id,
                "image": f"face_{i+1:03d}.png",
                "image_path": str(aligned_file),
            }
        )

    matrix = np.vstack(vectors).astype(np.float32)
    ids = store.add(matrix)

    metadata: list[dict] = []
    for idx, meta in zip(ids, payloads):
        meta["embedding_index"] = int(idx)
        id_map.set(idx, meta)
        metadata.append(
            {
                "embedding_index": int(idx),
                "image_path": meta["image_path"],
                "image_type": "KNOWN",
            }
        )

    store.save()
    id_map.save()
    return {
        "face_id": face_id,
        "user_id": user_id,
        "face_registered": True,
        "images": metadata,
    }


def delete_face(face_id: str, store: EmbeddingStore, id_map: IDMapStore) -> dict:
    remove_ids = id_map.find_indices_by_face_id(face_id)
    if not remove_ids:
        raise FaceException(404, "FACE_NOT_FOUND", "Face ID not found")

    old_map = id_map.data.copy()
    keep_keys = [k for k in sorted(old_map.keys(), key=lambda x: int(x)) if int(k) not in set(remove_ids)]
    keep_payloads = [old_map[k] for k in keep_keys]

    store.rebuild_without(remove_ids)

    id_map.data = {}
    for new_idx, payload in enumerate(keep_payloads):
        id_map.set(new_idx, payload)

    store.save()
    id_map.save()
    return {"status": "deleted", "face_id": face_id}
