# # modules/simple_skin_analyzer.py
# import cv2
# import numpy as np

# class SimpleSkinAnalyzer:
#     def __init__(self):
#         # Indian skin tones ke liye tuned HSV ranges
#         self.skin_hsv_lower = np.array([0, 30, 60], dtype="uint8")
#         self.skin_hsv_upper = np.array([25, 160, 255], dtype="uint8")

#     def analyze_skin(self, img_bgr):
#         """Skin tone, texture, foundation analysis."""
#         hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
#         skin_mask = cv2.inRange(hsv, self.skin_hsv_lower, self.skin_hsv_upper)
        
#         # Morphological cleaning
#         kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
#         skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
#         skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
#         skin_pixels = img_bgr[skin_mask > 0]
        
#         if len(skin_pixels) < 100:
#             return {
#                 "status": "low skin pixels detected",
#                 "skin_tone": "unknown",
#                 "texture": "unknown", 
#                 "foundation": "unknown",
#                 "skin_pixels": 0
#             }
        
#         # 1. Skin Tone (LAB L-channel)
#         lab_skin = cv2.cvtColor(skin_pixels, cv2.COLOR_BGR2LAB)
#         L_mean = np.mean(lab_skin[:,:,0])
        
#         if L_mean < 90:
#             skin_tone = "dark"
#         elif L_mean < 130:
#             skin_tone = "medium"
#         else:
#             skin_tone = "light"
        
#         # 2. Texture (grayscale standard deviation)
#         gray_skin = cv2.cvtColor(skin_pixels, cv2.COLOR_BGR2GRAY)
#         texture_std = np.std(gray_skin)
#         if texture_std < 12:
#             texture = "smooth"
#         elif texture_std < 25:
#             texture = "normal"
#         else:
#             texture = "textured"
        
#         # 3. Foundation (color uniformity)
#         color_std = np.std(skin_pixels, axis=0).mean()
#         if color_std < 18:
#             foundation = "heavy"
#         elif color_std < 35:
#             foundation = "light"
#         else:
#             foundation = "natural"
        
#         # Visualization with green overlay
#         output = img_bgr.copy()
#         output[skin_mask > 128] = [0, 255, 100]  # Green tint
        
#         # Labels
#         cv2.putText(output, f"Skin: {skin_tone}", (20, 50), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
#         cv2.putText(output, f"Texture: {texture}", (20, 90), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
#         cv2.putText(output, f"Foundation: {foundation}", (20, 130), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
#         return {
#             "output_image": output,
#             "skin_tone": skin_tone,
#             "texture": texture,
#             "foundation": foundation,
#             "skin_pixels": len(skin_pixels)
#         }
# modules/simple_skin_analyzer.py
import cv2
import numpy as np

class SimpleSkinAnalyzer:
    def __init__(self):
        self.skin_hsv_lower = np.array([0, 30, 60], dtype="uint8")
        self.skin_hsv_upper = np.array([25, 160, 255], dtype="uint8")

    def analyze_skin(self, img_bgr):
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(hsv, self.skin_hsv_lower, self.skin_hsv_upper)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
        skin_pixels = img_bgr[skin_mask > 0]
        
        if len(skin_pixels) < 100:
            return {"status": "low skin pixels", "skin_tone": "unknown", 
                   "texture": "unknown", "foundation": "unknown", "skin_pixels": 0}
        
        # ✅ FIXED: Convert pixels back to proper image format before cvtColor
        skin_img = skin_pixels.reshape(-1, 1, 3).astype(np.uint8)
        lab_skin = cv2.cvtColor(skin_img, cv2.COLOR_BGR2LAB)
        L_mean = np.mean(lab_skin[:,:,0])
        
        if L_mean < 90:
            skin_tone = "dark"
        elif L_mean < 130:
            skin_tone = "medium"
        else:
            skin_tone = "light"
        
        gray_skin = cv2.cvtColor(skin_img, cv2.COLOR_BGR2GRAY)
        texture_std = np.std(gray_skin)
        if texture_std < 12:
            texture = "smooth"
        elif texture_std < 25:
            texture = "normal"
        else:
            texture = "textured"
        
        color_std = np.std(skin_pixels, axis=0).mean()
        if color_std < 18:
            foundation = "heavy"
        elif color_std < 35:
            foundation = "light"
        else:
            foundation = "natural"
        
        output = img_bgr.copy()
        output[skin_mask > 128] = [0, 255, 100]
        
        cv2.putText(output, f"Skin: {skin_tone}", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(output, f"Texture: {texture}", (20, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(output, f"Foundation: {foundation}", (20, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        return {
            "output_image": output,
            "skin_tone": skin_tone,
            "texture": texture,
            "foundation": foundation,
            "skin_pixels": len(skin_pixels)
        }
