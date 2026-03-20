from __future__ import annotations

import base64
import threading
import time
from datetime import datetime, timezone

import cv2
import httpx

from app.core.config import settings
from app.models import Event, SystemConfig
import app.services.attendance_service as attendance_service
import app.services.face_metadata_service as face_metadata_service
import app.services.policy_service as policy_service
from app.services.camera_service import list_cameras
from app.core.database import SessionLocal


_workers: dict[str, "CameraWorker"] = {}
_lock = threading.Lock()
_wall_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_recent_camera_events: dict[tuple[str, str, str], float] = {}
_event_guard_lock = threading.Lock()


def _event(db, organization_id: str, event_type: str, severity: str, metadata: dict) -> None:
    db.add(
        Event(
            organization_id=organization_id,
            event_type=event_type,
            severity=severity,
            metadata_=metadata,
        )
    )
    db.commit()


def _validate_wall_frame(frame, min_face_area_ratio: float) -> tuple[bool, dict]:
    if frame is None:
        return False, {"reason": "empty_frame"}
    if _wall_face_cascade.empty():
        return False, {"reason": "haarcascade_not_loaded"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _wall_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(64, 64),
    )
    count = int(len(faces))
    if count != 1:
        return False, {"reason": "single_face_required", "faces_detected": count}

    x, y, w, h = faces[0]
    frame_area = float(frame.shape[0] * frame.shape[1])
    face_area_ratio = float((w * h) / frame_area) if frame_area > 0 else 0.0
    if face_area_ratio < float(min_face_area_ratio):
        return False, {
            "reason": "min_face_area_ratio_not_met",
            "faces_detected": count,
            "face_area_ratio": round(face_area_ratio, 4),
            "required_ratio": float(min_face_area_ratio),
        }

    return True, {
        "faces_detected": count,
        "face_area_ratio": round(face_area_ratio, 4),
        "required_ratio": float(min_face_area_ratio),
    }


class CameraWorker(threading.Thread):
    def __init__(self, organization_id: str, camera: dict):
        super().__init__(daemon=True, name=f"camera-worker-{camera['camera_id']}")
        self.organization_id = organization_id
        self.camera = camera
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        source = self.camera["source"]
        source_type = self.camera["camera_type"]
        camera_id = self.camera["camera_id"]
        direction = str(self.camera.get("direction", "both")).lower()
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            db = SessionLocal()
            try:
                _event(
                    db,
                    self.organization_id,
                    "CAMERA_OFFLINE",
                    "HIGH",
                    {"camera_id": camera_id, "source": source},
                )
            finally:
                db.close()
            return

        last_sample = 0.0
        while not self._stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.2)
                continue

            now = time.time()
            # Current policy is 1 FPS sampling for camera streams.
            if now - last_sample < 1.0:
                continue
            last_sample = now

            ok, enc = cv2.imencode(".jpg", frame)
            if not ok:
                continue
            b64 = base64.b64encode(enc.tobytes()).decode("utf-8")
            ts = datetime.now(timezone.utc)

            db = SessionLocal()
            try:
                policies = policy_service.get_effective_policies(db, self.organization_id)
                if source_type == "wall_camera":
                    min_face_area_ratio = float(policies.get("camera.wall.min_face_area_ratio", 0.5))
                    valid, detail = _validate_wall_frame(frame, min_face_area_ratio)
                    if not valid:
                        _event(
                            db,
                            self.organization_id,
                            "WALL_CAMERA_FRAME_SKIPPED",
                            "LOW",
                            {"camera_id": camera_id, **detail},
                        )
                        continue

                payload = {
                    "source_type": source_type,
                    "source_id": camera_id,
                    "timestamp": ts.isoformat(),
                    "image": f"data:image/jpeg;base64,{b64}",
                    "policy": policies,
                }
                try:
                    with httpx.Client(timeout=60.0) as client:
                        resp = client.post(f"{settings.FACE_SERVICE_URL}/faces/recognize", json=payload)
                    if not resp.is_success:
                        _event(
                            db,
                            self.organization_id,
                            "CAMERA_RECOGNITION_FAILED",
                            "MEDIUM",
                            {"camera_id": camera_id, "status_code": resp.status_code},
                        )
                        continue
                    result = resp.json()
                except Exception as exc:
                    _event(
                        db,
                        self.organization_id,
                        "CAMERA_RECOGNITION_ERROR",
                        "MEDIUM",
                        {"camera_id": camera_id, "error": str(exc)},
                    )
                    continue

                persist = face_metadata_service.persist_recognition_metadata(
                    db,
                    organization_id=self.organization_id,
                    captured_at=ts,
                    payload=result,
                )
                summary = self._mark_camera_attendance(
                    db=db,
                    result=result,
                    event_ts=ts.replace(tzinfo=None),
                    source_type=source_type,
                    camera_id=camera_id,
                    direction=direction,
                    threshold=float(policies.get("recognition.threshold", 0.8)),
                )
                _event(
                    db,
                    self.organization_id,
                    "CAMERA_FRAME_PROCESSED",
                    "LOW",
                    {"camera_id": camera_id, "persist": persist, "attendance": summary},
                )
            finally:
                db.close()

        cap.release()

    def _mark_camera_attendance(
        self,
        db,
        *,
        result: dict,
        event_ts,
        source_type: str,
        camera_id: str,
        direction: str,
        threshold: float,
    ) -> dict:
        rows = result.get("data", {}).get("results", [])
        matched_total = 0
        marked = 0
        skipped_low_confidence = 0
        skipped_duplicate = 0
        failed = 0

        event_type = "ENTRY" if direction == "entry" else "EXIT" if direction == "exit" else "ENTRY"
        now_ts = time.time()
        cooldown_sec = 30.0

        for row in rows:
            if row.get("status") != "matched":
                continue
            matched_total += 1

            user_id = row.get("user_id")
            confidence = float(row.get("confidence") or 0.0)
            if not user_id:
                failed += 1
                continue
            if confidence <= threshold:
                skipped_low_confidence += 1
                continue

            dedupe_key = (camera_id, user_id, event_type)
            with _event_guard_lock:
                last = _recent_camera_events.get(dedupe_key, 0.0)
                if (now_ts - last) < cooldown_sec:
                    skipped_duplicate += 1
                    continue
                _recent_camera_events[dedupe_key] = now_ts

            try:
                attendance_service.mark_camera_attendance_event(
                    db,
                    self.organization_id,
                    user_id=user_id,
                    event_type=event_type,
                    event_ts=event_ts,
                    source_type=source_type,
                    confidence=confidence,
                )
                marked += 1
            except Exception:
                failed += 1

        return {
            "matched_total": matched_total,
            "marked": marked,
            "skipped_low_confidence": skipped_low_confidence,
            "skipped_duplicate": skipped_duplicate,
            "failed": failed,
            "direction": direction,
            "event_type": event_type,
        }


def start_camera_worker(organization_id: str, camera: dict) -> dict:
    camera_id = camera["camera_id"]
    with _lock:
        existing = _workers.get(camera_id)
        if existing and existing.is_alive():
            return {"camera_id": camera_id, "status": "already_running"}
        worker = CameraWorker(organization_id, camera)
        _workers[camera_id] = worker
        worker.start()
        return {"camera_id": camera_id, "status": "started"}


def stop_camera_worker(camera_id: str) -> dict:
    with _lock:
        worker = _workers.get(camera_id)
        if worker is None:
            return {"camera_id": camera_id, "status": "not_running"}
        worker.stop()
        return {"camera_id": camera_id, "status": "stopping"}


def worker_status(camera_id: str) -> dict:
    with _lock:
        worker = _workers.get(camera_id)
        return {"camera_id": camera_id, "running": bool(worker and worker.is_alive())}


def all_worker_status() -> list[dict]:
    with _lock:
        return [{"camera_id": cid, "running": w.is_alive()} for cid, w in _workers.items()]


def bootstrap_enabled_workers(organization_id: str) -> None:
    db = SessionLocal()
    try:
        cameras = list_cameras(db, organization_id)
    finally:
        db.close()
    for camera in cameras:
        if camera.get("enabled"):
            start_camera_worker(organization_id, camera)


def bootstrap_all_enabled_workers() -> None:
    db = SessionLocal()
    try:
        rows = (
            db.query(SystemConfig)
            .filter(SystemConfig.config_key.like("camera.device.%"))
            .all()
        )
        items = [(str(r.organization_id), r.config_value or {}) for r in rows]
    finally:
        db.close()
    for org_id, camera in items:
        if camera.get("enabled"):
            start_camera_worker(org_id, camera)
