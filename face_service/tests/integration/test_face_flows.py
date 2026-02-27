import os
import unittest

os.environ["STORAGE_ROOT"] = "./storage_test"
os.environ["FAISS_INDEX_PATH"] = "./storage_test/embeddings/faiss.index"
os.environ["FAISS_ID_MAP_PATH"] = "./storage_test/embeddings/id_map.json"

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1 import faces as faces_api
from app.schemas.face import FaceResult, RecognizeResponse


class FaceServiceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._orig_register = faces_api.register_faces_service
        cls._orig_recognize = faces_api.recognize
        cls._orig_delete = faces_api.delete_face_service

        def fake_register(user_id, images, store, id_map):
            return {
                "face_id": f"face_{user_id}",
                "user_id": user_id,
                "face_registered": True,
                "images": [
                    {"embedding_index": 1, "image_path": f"storage/images/users/{user_id}/aligned/face_001.png", "image_type": "KNOWN"},
                    {"embedding_index": 2, "image_path": f"storage/images/users/{user_id}/aligned/face_002.png", "image_type": "KNOWN"},
                    {"embedding_index": 3, "image_path": f"storage/images/users/{user_id}/aligned/face_003.png", "image_type": "KNOWN"},
                ],
            }

        def fake_recognize(payload, matcher):
            return RecognizeResponse(
                source_type=payload.source_type,
                results=[
                    FaceResult(
                        face_index=0,
                        status="matched",
                        face_id="face_emp_001",
                        user_id="emp_001",
                        embedding_index=1,
                        image_path="storage/images/users/emp_001/aligned/face_001.png",
                        confidence=0.93,
                        action="entry_marked",
                    )
                ],
                errors=[],
            )

        def fake_delete(face_id, store, id_map):
            return {"status": "deleted", "face_id": face_id}

        faces_api.register_faces_service = fake_register
        faces_api.recognize = fake_recognize
        faces_api.delete_face_service = fake_delete

        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        faces_api.register_faces_service = cls._orig_register
        faces_api.recognize = cls._orig_recognize
        faces_api.delete_face_service = cls._orig_delete
        cls.client_ctx.__exit__(None, None, None)

    def test_register_recognize_delete_flow(self):
        c = self.client

        register = c.post(
            "/faces/register",
            data={"user_id": "emp_001"},
            files=[
                ("images", ("a.jpg", b"1", "image/jpeg")),
                ("images", ("b.jpg", b"2", "image/jpeg")),
                ("images", ("c.jpg", b"3", "image/jpeg")),
            ],
        )
        self.assertEqual(register.status_code, 200)
        self.assertEqual(register.json()["data"]["face_registered"], True)

        recognize = c.post(
            "/faces/recognize",
            json={
                "source_type": "camera",
                "source_id": "CAM_1",
                "timestamp": "2026-02-27T10:00:00",
                "image": "data:image/jpeg;base64,ZmFrZQ==",
            },
        )
        self.assertEqual(recognize.status_code, 200)
        self.assertEqual(recognize.json()["data"]["results"][0]["status"], "matched")

        delete = c.delete("/faces/face_emp_001")
        self.assertEqual(delete.status_code, 200)
        self.assertEqual(delete.json()["data"]["status"], "deleted")


if __name__ == "__main__":
    unittest.main()

