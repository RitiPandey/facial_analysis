# # modules/makeup_remover.py
# import cv2
# import numpy as np

# class MakeupRemover:
#     def __init__(self):
#         # Skin detection
#         self.skin_lower = np.array([0, 25, 50], dtype="uint8")
#         self.skin_upper = np.array([25, 160, 255], dtype="uint8")
        
#         # Lipstick (high saturation reds/pinks)
#         self.lip_lower = np.array([0, 100, 100], dtype="uint8")
#         self.lip_upper = np.array([15, 255, 255], dtype="uint8")
        
#         # Heavy foundation
#         self.foundation_lower = np.array([0, 20, 80], dtype="uint8")
#         self.foundation_upper = np.array([25, 80, 200], dtype="uint8")

#     def remove_makeup(self, img_bgr):
#         """Virtual makeup removal effect."""
#         original = img_bgr.copy()
        
#         # Skin mask for natural tone
#         hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#         skin_mask = cv2.inRange(hsv, self.skin_lower, self.skin_upper)
#         skin_pixels = img_bgr[skin_mask > 0]
        
#         if len(skin_pixels) < 20:
#             return original, np.zeros(img_bgr.shape[:2], dtype=np.uint8)
        
#         # Natural skin color
#         natural_skin = np.mean(skin_pixels, axis=0).astype(np.uint8)
        
#         # Detect lipstick
#         lip_mask = cv2.inRange(hsv, self.lip_lower, self.lip_upper)
#         kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
#         lip_mask = cv2.morphologyEx(lip_mask, cv2.MORPH_CLOSE, kernel_close)
        
#         # Detect heavy foundation
#         foundation_mask = cv2.inRange(hsv, self.foundation_lower, self.foundation_upper)
#         kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
#         foundation_mask = cv2.morphologyEx(foundation_mask, cv2.MORPH_OPEN, kernel_open)
        
#         # Combined makeup areas
#         makeup_mask = cv2.bitwise_or(lip_mask, foundation_mask)
#         makeup_mask = cv2.dilate(makeup_mask, 
#                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12)))
        
#         # Blend makeup areas with natural skin (60% original + 40% skin)
#         result = cv2.addWeighted(img_bgr, 0.6, 
#                                np.full_like(img_bgr, natural_skin), 0.4, 0)
        
#         # Apply only to makeup areas
#         mask_3d = makeup_mask[:,:,None].astype(bool)
#         result[mask_3d] = np.full((np.sum(mask_3d), 3), natural_skin, dtype=np.uint8)
        
#         # Face area enhancement (smooth oval)
#         h, w = img_bgr.shape[:2]
#         face_oval = np.zeros((h, w), dtype=np.uint8)
#         cv2.ellipse(face_oval, (w//2, h//2), (w//2.2, h//1.8), 0, 0, 360, 255, -1)
#         face_mask_smooth = cv2.GaussianBlur(face_oval, (51, 51), 0)
        
#         # Final enhancement
#         final_enhancement = 0.2 * (face_mask_smooth[:,:,None] / 255.0)
#         final_result = cv2.addWeighted(result, 1.0 - final_enhancement.max(), 
#                                      np.full_like(result, natural_skin), 
#                                      final_enhancement.max(), 0)
        
#         return final_result.astype(np.uint8), makeup_mask
# modules/makeup_remover.py
import cv2
import numpy as np

class MakeupRemover:
    def __init__(self):
        self.skin_lower = np.array([0, 25, 50], dtype="uint8")
        self.skin_upper = np.array([25, 160, 255], dtype="uint8")
        self.lip_lower = np.array([0, 100, 100], dtype="uint8")
        self.lip_upper = np.array([15, 255, 255], dtype="uint8")

    def remove_makeup(self, img_bgr):
        original = img_bgr.copy()
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Skin mask
        skin_mask = cv2.inRange(hsv, self.skin_lower, self.skin_upper)
        skin_pixels = img_bgr[skin_mask > 0]
        
        if len(skin_pixels) < 20:
            return original, np.zeros(img_bgr.shape[:2], dtype=np.uint8)
        
        natural_skin = np.mean(skin_pixels, axis=0).astype(np.uint8)
        
        # Lipstick detection
        lip_mask = cv2.inRange(hsv, self.lip_lower, self.lip_upper)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        lip_mask = cv2.morphologyEx(lip_mask, cv2.MORPH_CLOSE, kernel)
        
        # Foundation detection  
        foundation_mask = cv2.inRange(hsv, np.array([0, 20, 80]), np.array([25, 80, 200]))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        foundation_mask = cv2.morphologyEx(foundation_mask, cv2.MORPH_OPEN, kernel)
        
        # Combined makeup mask
        makeup_mask = cv2.bitwise_or(lip_mask, foundation_mask)
        makeup_mask = cv2.dilate(makeup_mask, 
                               cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12)))
        
        # ✅ FIXED: Use np.where instead of boolean indexing
        result = np.where(
            makeup_mask[:,:,None] > 128,
            natural_skin[None, None, :],
            img_bgr
        )
        
        # Face enhancement
        h, w = img_bgr.shape[:2]
        face_oval = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(face_oval, (w//2, h//2), (w//2.2, h//1.8), 0, 0, 360, 255, -1)
        face_mask_smooth = cv2.GaussianBlur(face_oval, (51, 51), 0)
        
        final_enhancement = 0.2 * (face_mask_smooth[:,:,None] / 255.0)
        final_result = (result * (1 - final_enhancement) + 
                       natural_skin[None, None, :] * final_enhancement).astype(np.uint8)
        
        return final_result, makeup_mask
