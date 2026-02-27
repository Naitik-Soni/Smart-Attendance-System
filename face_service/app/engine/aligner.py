import cv2
import numpy as np

class FaceAligner:
    def align(self, image: np.ndarray, box: list[int]) -> np.ndarray:
        # Simplistic crop and resize for now. 
        # A real aligner uses 5 points landmarks to rotate the face explicitly.
        
        x1, y1, x2, y2 = box
        
        # Expand box slightly
        pad = int((x2 - x1) * 0.1)
        
        h, w = image.shape[:2]
        
        crop_x1 = max(0, x1 - pad)
        crop_y1 = max(0, y1 - pad)
        crop_x2 = min(w, x2 + pad)
        crop_y2 = min(h, y2 + pad)
        
        cropped = image[crop_y1:crop_y2, crop_x1:crop_x2]
        
        # Arcface typically wants 112x112
        aligned = cv2.resize(cropped, (112, 112))
        return aligned

aligner = FaceAligner()
