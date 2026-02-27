import os
import unittest

# Set env before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_main_app.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["FACE_SERVICE_URL"] = "http://face-service.local"

from fastapi.testclient import TestClient

from app.main import app
from app.services import audit_service, auth_service, face_client, user_service


class MainAppIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.remove("test_main_app.db")
        except FileNotFoundError:
            pass

        cls._orig_recognize = face_client.recognize_faces
        cls._orig_register = face_client.register_faces

        cls._orig_auth_hash = auth_service.hash_password
        cls._orig_auth_verify = auth_service.verify_password
        cls._orig_user_hash = user_service.hash_password
        cls._orig_audit_write = audit_service.write_audit_log

        # Avoid external bcrypt backend issues during integration tests.
        auth_service.hash_password = lambda p: f"hash::{p}"
        auth_service.verify_password = lambda p, h: h == f"hash::{p}"
        user_service.hash_password = lambda p: f"hash::{p}"
        audit_service.write_audit_log = lambda *args, **kwargs: None

        async def fake_register(user_id, files):
            return {
                "success": True,
                "code": "FACE_REGISTERED",
                "data": {
                    "face_id": f"face_{user_id}",
                    "user_id": user_id,
                    "face_registered": True,
                    "images": [
                        {"embedding_index": 10, "image_path": "storage/images/users/%s/aligned/face_001.png" % user_id, "image_type": "KNOWN"},
                        {"embedding_index": 11, "image_path": "storage/images/users/%s/aligned/face_002.png" % user_id, "image_type": "KNOWN"},
                        {"embedding_index": 12, "image_path": "storage/images/users/%s/aligned/face_003.png" % user_id, "image_type": "KNOWN"},
                    ],
                },
                "meta": {"images_received": len(files)},
                "errors": [],
            }

        async def fake_recognize(source_type, source_id, timestamp, image):
            return {
                "success": True,
                "code": "FACE_RECOGNIZED",
                "data": {
                    "source_type": source_type,
                    "results": [
                        {
                            "face_index": 0,
                            "status": "matched",
                            "face_id": "face_emp_001",
                            "user_id": "emp_001",
                            "embedding_index": 10,
                            "image_path": "storage/images/users/emp_001/aligned/face_001.png",
                            "confidence": 0.95,
                            "action": "entry_marked",
                        },
                        {
                            "face_index": 1,
                            "status": "unknown",
                            "unknown_id": "unk_001",
                            "image_path": "storage/images/unknown/2026-02-27/CAM_1_unk_001.png",
                            "confidence": 0.4,
                            "action": "unknown_logged",
                        },
                    ],
                    "errors": [],
                },
                "meta": {"source_id": source_id},
                "errors": [],
            }

        face_client.register_faces = fake_register
        face_client.recognize_faces = fake_recognize

        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        auth_service.hash_password = cls._orig_auth_hash
        auth_service.verify_password = cls._orig_auth_verify
        user_service.hash_password = cls._orig_user_hash
        audit_service.write_audit_log = cls._orig_audit_write
        face_client.recognize_faces = cls._orig_recognize
        face_client.register_faces = cls._orig_register
        cls.client_ctx.__exit__(None, None, None)

    def test_full_auth_admin_ops_user_flow(self):
        c = self.client

        bootstrap = c.post(
            "/v1/auth/bootstrap-admin",
            json={
                "org_name": "Acme",
                "org_legal_name": "Acme Inc",
                "org_code": "ACME",
                "user_id": "admin1",
                "password": "StrongPass123",
                "name": "Admin One",
                "email": "admin@acme.com",
            },
        )
        self.assertEqual(bootstrap.status_code, 200)

        login = c.post("/v1/auth/login", json={"user_id": "admin1", "password": "StrongPass123"})
        self.assertEqual(login.status_code, 200)
        admin_tokens = login.json()["data"]["tokens"]

        refresh = c.post("/v1/auth/refresh", json={"refresh_token": admin_tokens["refresh_token"]})
        self.assertEqual(refresh.status_code, 200)
        admin_tokens = refresh.json()["data"]["tokens"]
        admin_auth = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

        add_operator = c.post(
            "/v1/admin/operator",
            headers=admin_auth,
            json={
                "operator_id": "op_001",
                "name": "Operator One",
                "email": "op1@acme.com",
                "password": "StrongPass123",
                "status": "active",
            },
        )
        self.assertEqual(add_operator.status_code, 200)

        op_login = c.post("/v1/auth/login", json={"user_id": "op_001", "password": "StrongPass123"})
        self.assertEqual(op_login.status_code, 200)
        op_auth = {"Authorization": f"Bearer {op_login.json()['data']['tokens']['access_token']}"}

        add_user = c.post(
            "/v1/ops/user",
            headers=op_auth,
            json={
                "user_id": "emp_001",
                "name": "Employee One",
                "email": "emp1@acme.com",
                "password": "StrongPass123",
                "role": "user",
                "status": "active",
            },
        )
        self.assertEqual(add_user.status_code, 200)

        upload_register = c.post(
            "/v1/ops/upload-image",
            headers=op_auth,
            data={"user_id": "emp_001"},
            files=[
                ("images", ("a.jpg", b"1", "image/jpeg")),
                ("images", ("b.jpg", b"2", "image/jpeg")),
                ("images", ("c.jpg", b"3", "image/jpeg")),
            ],
        )
        self.assertEqual(upload_register.status_code, 200)
        self.assertEqual(upload_register.json()["meta"]["images_persisted"], 3)

        upload_recognize = c.post(
            "/v1/ops/upload-image",
            headers=op_auth,
            data={"source_type": "camera", "source_id": "CAM_1"},
            files={"image": ("cam.jpg", b"raw", "image/jpeg")},
        )
        self.assertEqual(upload_recognize.status_code, 200)
        self.assertEqual(upload_recognize.json()["meta"]["images_persisted"], 2)

        manual = c.post(
            "/v1/ops/manual_attendance",
            headers=op_auth,
            json=[
                {
                    "user_id": "emp_001",
                    "attendance_type": "manual",
                    "status": "present",
                    "timestamp": "2026-02-27T09:00:00",
                    "reason": "manual test",
                }
            ],
        )
        self.assertEqual(manual.status_code, 200)

        emp_login = c.post("/v1/auth/login", json={"user_id": "emp_001", "password": "StrongPass123"})
        self.assertEqual(emp_login.status_code, 200)
        emp_auth = {"Authorization": f"Bearer {emp_login.json()['data']['tokens']['access_token']}"}

        get_attendance = c.get("/v1/user/get-attendance", headers=emp_auth)
        self.assertEqual(get_attendance.status_code, 200)
        self.assertGreaterEqual(len(get_attendance.json()["data"]), 1)

        logout = c.post(
            "/v1/auth/logout",
            headers=admin_auth,
            json={"refresh_token": admin_tokens["refresh_token"]},
        )
        self.assertEqual(logout.status_code, 200)

        after_logout = c.get("/v1/admin/system-health", headers=admin_auth)
        self.assertEqual(after_logout.status_code, 401)


if __name__ == "__main__":
    unittest.main()

