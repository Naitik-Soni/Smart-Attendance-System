import cv2
import numpy as np

class FaceAligner:
    @staticmethod
    def _rotate_point(M: np.ndarray, point: tuple[float, float]) -> tuple[int, int]:
        x, y = point
        new_x = M[0, 0] * x + M[0, 1] * y + M[0, 2]
        new_y = M[1, 0] * x + M[1, 1] * y + M[1, 2]
        return int(new_x), int(new_y)

    def _rotate_bbox(self, box: list[int], M: np.ndarray) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = box
        p1 = (x1, y1)
        p2 = (x2, y1)
        p3 = (x2, y2)
        p4 = (x1, y2)

        rp1 = self._rotate_point(M, p1)
        rp2 = self._rotate_point(M, p2)
        rp3 = self._rotate_point(M, p3)
        rp4 = self._rotate_point(M, p4)

        min_x = min(rp1[0], rp2[0], rp3[0], rp4[0])
        max_x = max(rp1[0], rp2[0], rp3[0], rp4[0])
        min_y = min(rp1[1], rp2[1], rp3[1], rp4[1])
        max_y = max(rp1[1], rp2[1], rp3[1], rp4[1])
        return min_x, min_y, max_x, max_y

    def align(self, image: np.ndarray, box: list[int], landmarks: dict | None = None) -> np.ndarray:
        x1, y1, x2, y2 = box

        if landmarks and "left_eye" in landmarks and "right_eye" in landmarks:
            left_eye = landmarks["left_eye"]
            right_eye = landmarks["right_eye"]
            dx = float(right_eye[0]) - float(left_eye[0])
            dy = float(right_eye[1]) - float(left_eye[1])
            angle = np.degrees(np.arctan2(dy, dx)) - 180.0
            eyes_center = (
                int((float(left_eye[0]) + float(right_eye[0])) / 2.0),
                int((float(left_eye[1]) + float(right_eye[1])) / 2.0),
            )
            M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
            image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]), flags=cv2.INTER_CUBIC)
            x1, y1, x2, y2 = self._rotate_bbox([x1, y1, x2, y2], M)

        pad = int((x2 - x1) * 0.1)
        h, w = image.shape[:2]
        crop_x1 = max(0, x1 - pad)
        crop_y1 = max(0, y1 - pad)
        crop_x2 = min(w, x2 + pad)
        crop_y2 = min(h, y2 + pad)

        cropped = image[crop_y1:crop_y2, crop_x1:crop_x2]
        if cropped.size == 0:
            cropped = image[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
        aligned = cv2.resize(cropped, (112, 112))
        return aligned

aligner = FaceAligner()
