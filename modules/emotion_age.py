# modules/emotion_age.py
import cv2
import numpy as np
from deepface import DeepFace
import warnings
warnings.filterwarnings('ignore')

class EmotionAgePipeline:
    def __init__(self):
        self.model_loaded = False
        
    def analyze_frame(self, image_bgr):
        out = image_bgr.copy()
        
        try:
            # DeepFace analysis (emotion + age + gender)
            analysis = DeepFace.analyze(image_bgr, actions=['emotion', 'age', 'gender'], 
                                      enforce_detection=False)
            
            # Extract results
            top_emotion = analysis[0]['dominant_emotion']
            age = analysis[0]['age']
            gender = analysis[0]['dominant_gender']
            
            # Draw results
            h, w = out.shape[:2]
            cv2.rectangle(out, (20, 20), (w-20, 100), (0, 0, 0), -1)
            cv2.putText(out, f"{top_emotion}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
            cv2.putText(out, f"Age: {age}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(out, f"Gender: {gender}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            emotions = analysis[0]['emotion']
            
        except:
            # Fallback if no face
            cv2.putText(out, "No face detected", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            top_emotion = "None"
            age = 0
            gender = "Unknown"
            emotions = {}
            
        return {
            "output_image": out,
            "top_emotion": top_emotion,
            "age": age,
            "gender": gender,
            "emotions": emotions
        }
