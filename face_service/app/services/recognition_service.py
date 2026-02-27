import base64
import uuid
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings
from app.core.exceptions import FaceException
from app.engine.aligner import aligner
from app.engine.detector import detector
from app.engine.embedder import embedder
from app.engine.matcher import FaceMatcher
from app.schemas.face import FaceResult, RecognizeRequest, RecognizeResponse


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
    path = Path(settings.STORAGE_ROOT) / "images" / "unknown" / d / f"{source_id}_{unknown_id}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image)
    return unknown_id, str(path)


def _action_for(source_type: str, status: str) -> str:
    if source_type == "upload_image":
        return "verification_only"
    if status == "matched":
        return "entry_marked"
    return "unknown_logged"


def recognize(payload: RecognizeRequest, matcher: FaceMatcher) -> RecognizeResponse:
    img = _decode_base64_image(payload.image)
    faces = detector.detect(img)
    if not faces:
        return RecognizeResponse(source_type=payload.source_type, results=[], errors=[{"code": "NO_FACE_DETECTED"}])

    results: list[FaceResult] = []
    for idx, found in enumerate(faces):
        aligned = aligner.align(img, found["box"])
        emb = embedder.embed(aligned)
        hit = matcher.match(emb, payload.source_type)
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

    return RecognizeResponse(source_type=payload.source_type, results=results, errors=[])
