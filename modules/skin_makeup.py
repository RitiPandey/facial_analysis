# # modules/skin_makeup.py
# import cv2
# import numpy as np
# from typing import Dict, Any
# import os

# class SkinMakeupAnalyzer:
#     def __init__(self):
#         # Skin HSV range
#         self.lower_hsv = np.array([0, 30, 60], dtype="uint8")
#         self.upper_hsv = np.array([20, 150, 255], dtype="uint8")
        
#         # Load Haar cascade for face detection
#         cascade_path = "models/haarcascade_frontalface_default.xml"
#         if os.path.exists(cascade_path):
#             self.face_cascade = cv2.CascadeClassifier(cascade_path)
#         else:
#             self.face_cascade = None
#             print("Warning: haarcascade_frontalface_default.xml not found")

#     def _detect_faces(self, img_bgr):
#         """Detect faces using Haar cascade."""
#         if self.face_cascade is None:
#             return []
        
#         gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
#         faces = self.face_cascade.detectMultiScale(
#             gray, scaleFactor=1.1, minNeighbors=5, 
#             minSize=(30, 30)
#         )
#         return faces

#     def _get_skin_mask(self, img_bgr):
#         hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#         mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
#         # Morphological operations
#         kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
#         return mask

#     def _remove_makeup(self, img_bgr, skin_mask, faces):
#         """Simple makeup removal: replace heavy makeup areas with average skin tone."""
#         makeup_removed = img_bgr.copy()
        
#         if len(faces) > 0:
#             # Average skin color from face region
#             face_region = img_bgr[faces[0][1]:faces[0][1]+faces[0][3], 
#                                 faces[0][0]:faces[0][0]+faces[0][2]]
#             skin_in_face = face_region[skin_mask[faces[0][1]:faces[0][1]+faces[0][3], 
#                                                faces[0][0]:faces[0][0]+faces[0][2]] > 0]
            
#             if len(skin_in_face) > 10:
#                 avg_skin_color = np.mean(skin_in_face, axis=0).astype(np.uint8)
#             else:
#                 avg_skin_color = np.array([200, 150, 120])  # fallback beige
        
#         else:
#             skin_pixels = img_bgr[skin_mask > 0]
#             if len(skin_pixels) > 10:
#                 avg_skin_color = np.mean(skin_pixels, axis=0).astype(np.uint8)
#             else:
#                 avg_skin_color = np.array([200, 150, 120])

#         # Apply to heavy makeup areas (low skin confidence + high saturation)
#         hsv_full = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#         high_sat_mask = hsv_full[:,:,1] > 100  # High saturation = possible makeup
#         makeup_mask = (skin_mask < 128) & high_sat_mask
        
#         # Blend makeup areas with skin color
#         makeup_mask_3d = np.stack([makeup_mask]*3, axis=-1)
#         makeup_removed[makeup_mask_3d] = avg_skin_color
        
#         return makeup_removed

#     def analyze(self, img_bgr) -> Dict[str, Any]:
#         original = img_bgr.copy()
#         h, w = img_bgr.shape[:2]
        
#         # 1. Face detection (RED BORDER!)
#         faces = self._detect_faces(img_bgr)
        
#         # 2. Skin analysis
#         skin_mask = self._get_skin_mask(img_bgr)
#         skin_pixels = img_bgr[skin_mask > 0]
        
#         # Basic analysis
#         skin_tone = "unknown"
#         if len(skin_pixels) > 50:
#             lab = cv2.cvtColor(np.array([skin_pixels], dtype=np.uint8), cv2.COLOR_BGR2LAB)[0]
#             L_mean = lab[:, 0].mean() / 255.0
#             if L_mean < 0.45:
#                 skin_tone = "dark"
#             elif L_mean < 0.65:
#                 skin_tone = "medium"
#             else:
#                 skin_tone = "light"
        
#         # 3. Makeup removal
#         makeup_removed = self._remove_makeup(img_bgr, skin_mask, faces)
        
#         # 4. Draw everything on original
#         output = original.copy()
        
#         # RED FACE BORDER (main cheez!)
#         for (x, y, fx, fy) in faces:
#             cv2.rectangle(output, (x, y), (x+fx, y+fy), (0, 0, 255), 3)  # RED!
#             cv2.putText(output, "FACE", (x, y-10), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
#         # Skin mask visualization (green overlay)
#         skin_overlay = output.copy()
#         skin_overlay[skin_mask > 128] = [0, 255, 0]  # Green tint on skin
        
#         # Blend skin overlay
#         output = cv2.addWeighted(output, 0.7, skin_overlay, 0.3, 0)
        
#         # Text overlay
#         cv2.putText(output, f"Skin: {skin_tone}", (10, 30), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
#         cv2.putText(output, f"Faces: {len(faces)}", (10, 65), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
#         cv2.putText(output, "MAKEUP REMOVED", (10, 100), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        
#         return {
#             "output_image": output,
#             "makeup_removed": makeup_removed,
#             "original_image": original,
#             "faces_detected": len(faces),
#             "skin_tone": skin_tone,
#             "skin_mask": skin_mask,
#         }
# modules/skin_makeup.py
import cv2
import numpy as np
from typing import Dict, Any
import os

class SkinMakeupAnalyzer:
    def __init__(self):
        self.lower_hsv = np.array([0, 30, 60], dtype="uint8")
        self.upper_hsv = np.array([20, 150, 255], dtype="uint8")
        
        cascade_path = "models/haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        else:
            self.face_cascade = None

    def _detect_faces(self, img_bgr):
        if self.face_cascade is None:
            return []
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return faces

    def _get_skin_mask(self, img_bgr):
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        return mask

    def _remove_makeup(self, img_bgr, skin_mask, faces):  # ✅ FIXED VERSION
        makeup_removed = img_bgr.copy()
        
        # Average skin color
        skin_pixels = img_bgr[skin_mask > 0]
        if len(skin_pixels) > 10:
            avg_skin_color = np.mean(skin_pixels, axis=0).astype(np.uint8)
        else:
            avg_skin_color = np.array([200, 150, 120])
        
        # High saturation = possible makeup
        hsv_full = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        high_sat_mask = (hsv_full[:,:,1] > 80) & (skin_mask < 100)
        
        # ✅ CORRECT: np.where handles broadcasting automatically
        makeup_removed = np.where(
            high_sat_mask[:,:,None],
            avg_skin_color[None, None, :],
            makeup_removed
        )
        
        return makeup_removed.astype(np.uint8)

    def analyze(self, img_bgr) -> Dict[str, Any]:
        original = img_bgr.copy()
        h, w = img_bgr.shape[:2]
        
        # Face detection (RED BORDER)
        faces = self._detect_faces(img_bgr)
        skin_mask = self._get_skin_mask(img_bgr)
        skin_pixels = img_bgr[skin_mask > 0]
        
        # Skin tone
        skin_tone = "unknown"
        if len(skin_pixels) > 50:
            lab = cv2.cvtColor(np.array([skin_pixels], dtype=np.uint8), cv2.COLOR_BGR2LAB)[0]
            L_mean = lab[:, 0].mean() / 255.0
            if L_mean < 0.45: skin_tone = "dark"
            elif L_mean < 0.65: skin_tone = "medium"
            else: skin_tone = "light"
        
        # Makeup removal
        makeup_removed = self._remove_makeup(img_bgr, skin_mask, faces)
        
        # Draw on original
        output = original.copy()
        
        # RED FACE BORDER!
        for (x, y, fx, fy) in faces:
            cv2.rectangle(output, (x, y), (x+fx, y+fy), (0, 0, 255), 3)
            cv2.putText(output, "FACE", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Skin overlay (green tint)
        skin_overlay = output.copy()
        skin_overlay[skin_mask > 128] = [0, 255, 0]
        output = cv2.addWeighted(output, 0.7, skin_overlay, 0.3, 0)
        
        # Labels
        cv2.putText(output, f"Skin: {skin_tone}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(output, f"Faces: {len(faces)}", (10, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(output, "MAKEUP REMOVED", (10, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        
        return {
            "output_image": output,
            "makeup_removed": makeup_removed,
            "original_image": original,
            "faces_detected": len(faces),
            "skin_tone": skin_tone,
        }

