import cv2
import numpy as np
from ..core.exceptions import FaceException

class FaceDetector:
    def __init__(self):
        # We use OpenCV's built-in Haar Cascade for dev/simplicity
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect(self, image: np.ndarray):
        # image expected as uncompressed numpy array (BGR from cv2.imdecode)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Blur check using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50.0: # Arbitrary threshold for "blurry"
             raise FaceException(400, "IMAGE_BLURRY", f"Image is too blurry {laplacian_var:.2f}")

        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        
        results = []
        for (x, y, w, h) in faces:
            results.append({
                "box": [int(x), int(y), int(x+w), int(y+h)],
                "score": 0.99 # Mock confidence for Haar cascade
            })
            
        return results

detector = FaceDetector()
