import io
import unittest
from datetime import datetime

import cv2
import numpy as np
from fastapi import UploadFile

from app.core.exceptions import FaceException
from app.engine.matcher import FaceMatcher
from app.schemas.face import RecognizeRequest
from app.services import recognition_service, registration_service


class _DummyStore:
    class _Index:
        ntotal = 1

    def __init__(self):
        self.index = self._Index()

    def search(self, embedding, top_k=1):
        return np.array([[0.5]], dtype=np.float32), np.array([[1]], dtype=np.int64)


class _DummyIdMap:
    def get(self, idx):
        return {"user_id": "emp_001", "face_id": "face_emp_001", "embedding_index": idx}


class _DummyMatcher:
    def match(self, embedding, source_type, threshold_override=None):
        return {"status": "matched", "confidence": 0.99, "payload": {"user_id": "emp_001", "face_id": "face_emp_001"}}


class PolicyRuleTests(unittest.TestCase):
    def test_threshold_is_strictly_greater(self):
        matcher = FaceMatcher(_DummyStore(), _DummyIdMap())
        hit = matcher.match(np.zeros((512,), dtype=np.float32), "wall_camera", threshold_override=0.5)
        self.assertEqual(hit["status"], "unknown")

    def test_wall_camera_ratio_rejects_face(self):
        original_decode = recognition_service._decode_base64_image
        original_detect = recognition_service.detector.detect
        original_align = recognition_service.aligner.align
        original_embed = recognition_service.embedder.embed
        try:
            recognition_service._decode_base64_image = lambda _: np.zeros((100, 100, 3), dtype=np.uint8)
            recognition_service.detector.detect = lambda img, min_laplacian_variance=None: [{"box": [0, 0, 10, 10]}]
            recognition_service.aligner.align = lambda img, box: img
            recognition_service.embedder.embed = lambda aligned: np.zeros((512,), dtype=np.float32)

            payload = RecognizeRequest(
                source_type="wall_camera",
                source_id="CAM_1",
                timestamp=datetime.utcnow(),
                image="data:image/jpeg;base64,ZmFrZQ==",
                policy={"camera.wall.min_face_area_ratio": 0.5},
            )
            out = recognition_service.recognize(payload, _DummyMatcher())
            self.assertEqual(out.results[0].status, "unknown")
            self.assertEqual(out.errors[0]["code"], "WALL_FACE_RATIO_TOO_LOW")
        finally:
            recognition_service._decode_base64_image = original_decode
            recognition_service.detector.detect = original_detect
            recognition_service.aligner.align = original_align
            recognition_service.embedder.embed = original_embed

    def test_registration_rejects_multiple_faces(self):
        original_detect = registration_service.detector.detect
        original_save = registration_service._save_image
        try:
            registration_service.detector.detect = lambda img, min_laplacian_variance=None: [
                {"box": [10, 10, 130, 130]},
                {"box": [140, 10, 260, 130]},
            ]
            registration_service._save_image = lambda image, path: None

            img = np.zeros((800, 800, 3), dtype=np.uint8)
            ok, encoded = cv2.imencode(".jpg", img)
            self.assertTrue(ok)
            upload = UploadFile(filename="sample.jpg", file=io.BytesIO(encoded.tobytes()))

            with self.assertRaises(FaceException) as exc:
                registration_service.register_faces(
                    user_id="emp_001",
                    images=[upload, upload, upload],
                    store=None,
                    id_map=None,
                    policies={
                        "enrollment.images.min_count": 3,
                        "enrollment.images.max_count": 5,
                        "quality.min_image_width": 10,
                        "quality.min_image_height": 10,
                        "quality.min_laplacian_variance": 0,
                        "quality.min_face_width_px": 10,
                        "quality.min_face_height_px": 10,
                    },
                )
            self.assertEqual(exc.exception.code, "MULTIPLE_FACES_IN_ENROLLMENT")
        finally:
            registration_service.detector.detect = original_detect
            registration_service._save_image = original_save


if __name__ == "__main__":
    unittest.main()
