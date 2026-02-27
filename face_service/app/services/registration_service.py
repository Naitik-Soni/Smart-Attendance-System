import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FaceException
from app.engine.aligner import aligner
from app.engine.detector import detector
from app.engine.embedder import embedder
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
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise FaceException(500, "WRITE_FAILED", f"Failed to write image '{path.name}'")


def register_faces(
    user_id: str,
    images: list[UploadFile],
    store: EmbeddingStore,
    id_map: IDMapStore,
) -> dict:
    if not 3 <= len(images) <= 5:
        raise FaceException(400, "INVALID_IMAGE_COUNT", "Provide 3 to 5 images")

    face_id = f"face_{user_id}"
    vectors = []
    payloads = []
    user_root = Path(settings.STORAGE_ROOT) / "images" / "users" / user_id
    original_dir = user_root / "original"
    aligned_dir = user_root / "aligned"

    for i, upload in enumerate(images):
        img = _decode_upload(upload)
        _save_image(img, original_dir / f"img_{i+1:03d}.jpg")

        faces = detector.detect(img)
        if not faces:
            raise FaceException(400, "NO_FACE_DETECTED", f"No face detected in '{upload.filename}'")

        best = faces[0]
        aligned = aligner.align(img, best["box"])
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
