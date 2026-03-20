import base64
import uuid
from datetime import datetime

import cv2
import numpy as np

from app.core.config import settings
from app.core.exceptions import FaceException
from app.engine.aligner import aligner
from app.engine.detector import detector
from app.engine.embedder import embedder
from app.engine.matcher import FaceMatcher
from app.schemas.face import FaceResult, RecognizeRequest, RecognizeResponse
from app.storage import get_storage_backend


def _decode_base64_image(data: str) -> np.ndarray:
    encoded = data.split(",", 1)[1] if "," in data else data
    try:
        raw = base64.b64decode(encoded)
    except Exception as exc:
        raise FaceException(400, "INVALID_IMAGE", "Invalid base64 image") from exc

    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise FaceException(400, "INVALID_IMAGE", "Could not decode base64 image")
    return img


def _save_unknown_face(image: np.ndarray, source_id: str, when: datetime) -> tuple[str, str]:
    unknown_id = f"unk_{uuid.uuid4().hex[:8]}"
    d = when.strftime("%Y-%m-%d")
    relative_path = f"images/unknown/{d}/{source_id}_{unknown_id}.png"
    stored = get_storage_backend().save_image(image, relative_path)
    return unknown_id, stored


def _action_for(source_type: str, status: str) -> str:
    if source_type == "upload_image":
        return "verification_only"
    if status == "matched":
        return "entry_marked"
    return "unknown_logged"


def _face_area_ratio(img: np.ndarray, box: list[int]) -> float:
    x1, y1, x2, y2 = box
    face_area = max(x2 - x1, 0) * max(y2 - y1, 0)
    frame_area = max(img.shape[0] * img.shape[1], 1)
    return float(face_area) / float(frame_area)


def _policy_float(policies: dict | None, key: str, fallback: float) -> float:
    if not policies or key not in policies:
        return float(fallback)
    try:
        return float(policies[key])
    except Exception:
        return float(fallback)


def recognize(payload: RecognizeRequest, matcher: FaceMatcher) -> RecognizeResponse:
    img = _decode_base64_image(payload.image)
    blur_threshold = _policy_float(payload.policy, "quality.min_laplacian_variance", settings.QUALITY_MIN_LAPLACIAN_VARIANCE)
    faces = detector.detect(img, min_laplacian_variance=blur_threshold)
    if not faces:
        return RecognizeResponse(source_type=payload.source_type, results=[], errors=[{"code": "NO_FACE_DETECTED"}])

    results: list[FaceResult] = []
    errors: list[dict] = []
    for idx, found in enumerate(faces):
        if payload.source_type == "wall_camera":
            ratio = _face_area_ratio(img, found["box"])
            wall_min_ratio = _policy_float(payload.policy, "camera.wall.min_face_area_ratio", settings.WALL_MIN_FACE_AREA_RATIO)
            if ratio <= wall_min_ratio:
                errors.append(
                    {
                        "code": "WALL_FACE_RATIO_TOO_LOW",
                        "face_index": idx,
                        "min_ratio": wall_min_ratio,
                        "observed_ratio": round(ratio, 4),
                    }
                )
                results.append(
                    FaceResult(
                        face_index=idx,
                        status="unknown",
                        confidence=None,
                        action="ignored",
                    )
                )
                continue

        aligned = aligner.align(img, found["box"], found.get("landmarks"))
        emb = embedder.embed(aligned)
        threshold = _policy_float(payload.policy, "recognition.threshold", settings.CONFIDENCE_THRESHOLD)
        hit = matcher.match(emb, payload.source_type, threshold_override=threshold)
        if hit["status"] == "matched":
            meta = hit["payload"]
            results.append(
                FaceResult(
                    face_index=idx,
                    status="matched",
                    face_id=meta.get("face_id"),
                    user_id=meta.get("user_id"),
                    embedding_index=meta.get("embedding_index"),
                    image_path=meta.get("image_path"),
                    confidence=round(float(hit["confidence"]), 4),
                    action=_action_for(payload.source_type, "matched"),
                )
            )
        else:
            unknown_id, unknown_path = _save_unknown_face(aligned, payload.source_id, payload.timestamp)
            results.append(
                FaceResult(
                    face_index=idx,
                    status="unknown",
                    unknown_id=unknown_id,
                    image_path=unknown_path,
                    confidence=round(float(hit["confidence"]), 4) if hit["confidence"] is not None else None,
                    action=_action_for(payload.source_type, "unknown"),
                )
            )

    return RecognizeResponse(source_type=payload.source_type, results=results, errors=errors)
