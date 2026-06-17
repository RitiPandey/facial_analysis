# import cv2
# import numpy as np
# import mediapipe as mp
# from typing import Dict, Any, List, Tuple
# import warnings
# warnings.filterwarnings('ignore')

# mp_face_mesh = mp.solutions.face_mesh
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles

# class LivenessPipeline:
#     def __init__(self):
#         """Easier thresholds for reliable detection"""
#         self.face_mesh = mp_face_mesh.FaceMesh(
#             max_num_faces=1,
#             refine_landmarks=True,
#             min_detection_confidence=0.5,  # Lower for easier detection
#             min_tracking_confidence=0.5    # Lower for easier detection
#         )
        
#         # Easier blink thresholds (works better in practice)
#         self.ear_open_threshold = 0.22      # Eyes must be > this to be "open"
#         self.ear_blink_threshold = 0.15     # Eyes < this = "closed"
        
#         # State tracking
#         self._ear_history = []
#         self._blink_count = 0
#         self._last_nose_pos = None
        
#         # Eye landmark indices (MediaPipe FaceMesh)
#         self.left_eye = [33, 160, 158, 133, 153, 144]
#         self.right_eye = [362, 385, 387, 263, 373, 380]
#         self.nose_tip = 1

#     def _get_landmark_point(self, landmarks, idx, width, height):
#         """Convert normalized landmark to pixel coordinates"""
#         x = landmarks[idx].x * width
#         y = landmarks[idx].y * height
#         return (int(x), int(y))

#     def _euclidean_distance(self, point1, point2):
#         """Calculate distance between two points"""
#         return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

#     def _calculate_ear(self, landmarks, eye_indices, width, height):
#         """Eye Aspect Ratio (EAR) calculation"""
#         try:
#             # Get eye points
#             eye_points = [self._get_landmark_point(landmarks, idx, width, height) 
#                          for idx in eye_indices]
            
#             # Vertical distances (A-B, C-D)
#             vertical_dist1 = self._euclidean_distance(eye_points[1], eye_points[5])
#             vertical_dist2 = self._euclidean_distance(eye_points[2], eye_points[4])
            
#             # Horizontal distance (E-F)
#             horizontal_dist = self._euclidean_distance(eye_points[0], eye_points[3])
            
#             # EAR = (|A-B| + |C-D|) / (2 * |E-F|)
#             ear = (vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)
#             return ear
#         except:
#             return 0.0

#     def analyze_frame(self, image_bgr: np.ndarray) -> Dict[str, Any]:
#         """Main analysis function"""
#         rgb_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
#         results = self.face_mesh.process(rgb_image)
        
#         output_image = image_bgr.copy()
#         height, width = output_image.shape[:2]
        
#         # Default values
#         avg_ear = 0.0
#         blink_detected = False
#         eyes_open = False
#         movement = 0.0
#         is_live = False
#         blink_count = self._blink_count

#         if results.multi_face_landmarks:
#             face_landmarks = results.multi_face_landmarks[0]
            
#             # Draw face mesh
#             mp_drawing.draw_landmarks(
#                 image=output_image,
#                 landmark_list=face_landmarks,
#                 connections=mp_face_mesh.FACEMESH_TESSELATION,
#                 landmark_drawing_spec=None,
#                 connection_drawing_spec=mp_drawing_styles
#                 .get_default_face_mesh_tesselation_style()
#             )

#             # Calculate EAR for both eyes
#             left_ear = self._calculate_ear(face_landmarks.landmark, self.left_eye, width, height)
#             right_ear = self._calculate_ear(face_landmarks.landmark, self.right_eye, width, height)
#             avg_ear = (left_ear + right_ear) / 2.0

#             # Track EAR history (last 8 frames)
#             self._ear_history.append(avg_ear)
#             self._ear_history = self._ear_history[-8:]

#             # Blink detection: open → closed → open pattern
#             blink_detected = False
#             if len(self._ear_history) >= 4:
#                 recent_ears = self._ear_history[-4:]
#                 # Pattern: high → low → high (open-close-open)
#                 if (recent_ears[0] > self.ear_open_threshold and 
#                     recent_ears[1] < self.ear_blink_threshold and 
#                     recent_ears[2] > self.ear_open_threshold):
#                     blink_detected = True
#                     self._blink_count += 1

#             # Eyes state
#             eyes_open = avg_ear > self.ear_open_threshold

#             # Head movement (nose position change)
#             nose_point = self._get_landmark_point(face_landmarks.landmark, self.nose_tip, width, height)
#             if self._last_nose_pos:
#                 movement = self._euclidean_distance(self._last_nose_pos, nose_point)
#             self._last_nose_pos = nose_point

#             # Liveness decision (easier rules)
#             is_live = (self._blink_count > 0 or 
#                       (eyes_open and movement > 1.0) or 
#                       movement > 2.5)

#             # Draw results on image
#             status = "✅ LIVE" if is_live else "🔄 BLINK/MOVE"
#             color = (0, 255, 0) if is_live else (0, 165, 255)
            
#             cv2.rectangle(output_image, (10, 10), (400, 120), (0, 0, 0), -1)
#             cv2.putText(output_image, status, (20, 40), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
#             cv2.putText(output_image, f"EAR: {avg_ear:.3f}", (20, 70), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
#             cv2.putText(output_image, f"Movement: {movement:.1f}px", (20, 95), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
#             cv2.putText(output_image, f"Blinks: {self._blink_count}", (20, 120), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

#         return {
#             "output_image": output_image,
#             "avg_ear": float(avg_ear),
#             "blink_detected": blink_detected,
#             "eyes_open": eyes_open,
#             "movement": float(movement),
#             "is_live": is_live,
#             "blink_count": self._blink_count
#         }
# modules/liveness.py
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Any

mp_face_mesh = mp.solutions.face_mesh

class LivenessPipeline:
    def __init__(self):
        # yahan FaceMesh ek baar banayenge, default flags se
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # EAR ke liye landmark indices
        self.left_eye = [33, 160, 158, 133, 153, 144]
        self.right_eye = [362, 385, 387, 263, 373, 380]
        self.nose_tip = 1

        # thresholds
        self.ear_open_thr = 0.22
        self.ear_blink_thr = 0.15

        # state
        self._ear_hist = []
        self._blink_count = 0
        self._last_nose_pos = None

    def _lm_xy(self, lm, w, h):
        return int(lm.x * w), int(lm.y * h)

    def _dist(self, p1, p2):
        return float(np.linalg.norm(np.array(p1) - np.array(p2)))

    def _ear(self, landmarks, idxs, w, h):
        pts = [self._lm_xy(landmarks[i], w, h) for i in idxs]
        v1 = self._dist(pts[1], pts[5])
        v2 = self._dist(pts[2], pts[4])
        hdist = self._dist(pts[0], pts[3])
        if hdist == 0:
            return 0.0
        return (v1 + v2) / (2.0 * hdist)

    def analyze_frame(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """Blink + head movement based liveness."""
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        out = img_bgr.copy()
        h, w = out.shape[:2]

        avg_ear = 0.0
        blink_now = False
        eyes_open = False
        movement = 0.0
        is_live = False

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]

            # EAR
            left_ear = self._ear(face.landmark, self.left_eye, w, h)
            right_ear = self._ear(face.landmark, self.right_eye, w, h)
            avg_ear = (left_ear + right_ear) / 2.0

            self._ear_hist.append(avg_ear)
            self._ear_hist = self._ear_hist[-8:]

            if len(self._ear_hist) >= 4:
                e0, e1, e2, _ = self._ear_hist[-4:]
                if e0 > self.ear_open_thr and e1 < self.ear_blink_thr and e2 > self.ear_open_thr:
                    blink_now = True
                    self._blink_count += 1

            eyes_open = avg_ear > self.ear_open_thr

            # head movement (nose tip)
            nose = self._lm_xy(face.landmark[self.nose_tip], w, h)
            if self._last_nose_pos is not None:
                movement = self._dist(self._last_nose_pos, nose)
            self._last_nose_pos = nose

            # simple liveness rule
            is_live = (self._blink_count > 0) or (eyes_open and movement > 1.0) or movement > 2.5

            # draw overlay
            status = "LIVE" if is_live else "BLINK / MOVE"
            color = (0, 255, 0) if is_live else (0, 165, 255)

            cv2.rectangle(out, (10, 10), (420, 120), (0, 0, 0), -1)
            cv2.putText(out, status, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(out, f"EAR: {avg_ear:.3f}", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(out, f"Move: {movement:.1f}", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return {
            "output_image": out,
            "avg_ear": float(avg_ear),
            "blink_detected": blink_now,
            "eyes_open": eyes_open,
            "movement": float(movement),
            "is_live": is_live,
            "blink_count": int(self._blink_count),
        }
