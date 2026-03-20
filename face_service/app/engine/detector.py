import cv2
import numpy as np
from app.core.config import settings
from ..core.exceptions import FaceException

try:
    from retinaface import RetinaFace  # type: ignore
except Exception:  # pragma: no cover
    RetinaFace = None

class FaceDetector:
    def __init__(self):
        # Fallback detector used when RetinaFace package is unavailable.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect(self, image: np.ndarray, min_laplacian_variance: float | None = None):
        # image expected as uncompressed numpy array (BGR from cv2.imdecode)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blur check using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        threshold = float(min_laplacian_variance) if min_laplacian_variance is not None else float(settings.QUALITY_MIN_LAPLACIAN_VARIANCE)
        if laplacian_var < threshold:
             raise FaceException(400, "IMAGE_QUALITY_TOO_LOW", f"Image blur variance too low: {laplacian_var:.2f}")

        if RetinaFace is not None:
            detected = RetinaFace.detect_faces(image)
            if not isinstance(detected, dict):
                return []
            results = []
            for face in detected.values():
                facial_area = face.get("facial_area")
                if not facial_area or len(facial_area) != 4:
                    continue
                results.append(
                    {
                        "box": [int(facial_area[0]), int(facial_area[1]), int(facial_area[2]), int(facial_area[3])],
                        "score": float(face.get("score", 0.0)),
                        "landmarks": face.get("landmarks") or {},
                    }
                )
            return results

        if not settings.RETINAFACE_FALLBACK_TO_HAAR:
            raise FaceException(500, "RETINAFACE_UNAVAILABLE", "RetinaFace dependency is not installed")

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
        )

        results = []
        for (x, y, w, h) in faces:
            results.append(
                {
                    "box": [int(x), int(y), int(x + w), int(y + h)],
                    "score": 0.99,
                    "landmarks": {},
                }
            )
        return results

detector = FaceDetector()
