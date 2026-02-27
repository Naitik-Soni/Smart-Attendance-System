from pathlib import Path

import numpy as np

from app.core.config import settings

try:
    import onnxruntime as ort
except Exception:  # pragma: no cover
    ort = None


class FaceEmbedder:
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH)
        self.session = None
        self.input_name = None
        self.dev_mode = True

        if ort is not None and self.model_path.exists():
            self.session = ort.InferenceSession(str(self.model_path), providers=["CPUExecutionProvider"])
            self.input_name = self.session.get_inputs()[0].name
            self.dev_mode = False

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(v, axis=1, keepdims=True) + 1e-9
        return v / n

    def embed(self, aligned_face: np.ndarray) -> np.ndarray:
        if self.dev_mode:
            v = np.random.randn(1, settings.EMBEDDING_DIM).astype(np.float32)
            return self._normalize(v)[0]

        img = aligned_face.astype(np.float32)
        img = (img - 127.5) / 128.0
        img = np.transpose(img, (2, 0, 1))[None, ...]
        out = self.session.run(None, {self.input_name: img})[0]
        out = out.astype(np.float32)
        return self._normalize(out)[0]


embedder = FaceEmbedder()
