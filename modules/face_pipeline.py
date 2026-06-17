# modules/face_pipeline.py
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any

mp_fd = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

class FacePipeline:
    def __init__(self, min_conf: float = 0.5):
        self.detector = mp_fd.FaceDetection(
            model_selection=1, min_detection_confidence=min_conf
        )

    def analyze_frame(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """Run face detection on a single BGR frame."""
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)

        out = image_bgr.copy()
        faces = []

        if results.detections:
            h, w, _ = out.shape
            for det in results.detections:
                mp_draw.draw_detection(out, det)
                bbox = det.location_data.relative_bounding_box
                faces.append({
                    "confidence": float(det.score[0]),
                    "bbox": {
                        "xmin": bbox.xmin * w,
                        "ymin": bbox.ymin * h,
                        "width": bbox.width * w,
                        "height": bbox.height * h,
                    },
                })

        return {
            "output_image": out,
            "faces": faces,
        }
