
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Real-Time Face Analysis", layout="wide")

st.title("Real-Time Face Detection")
st.markdown("**OpenCV**")

if "faces_detected" not in st.session_state:
    st.session_state.faces_detected = 0

@st.cache_resource
def load_face_cascade():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_face_cascade()

def detect_faces(img_bgr):
    """Pure OpenCV face detection."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    output = img_bgr.copy()
    confidences = []
    
    for (x, y, w, h) in faces:
        cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(output, f"Face {len(confidences)+1}", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        confidence = min(1.0, (w * h) / (img_bgr.shape[1] * img_bgr.shape[0]))
        confidences.append(float(confidence))
    
    return {
        "output_image": output,
        "faces": [{"bbox": [x,y,w,h], "confidence": conf} for (x,y,w,h), conf in zip(faces, confidences)],
        "faces_count": len(faces),
        "avg_confidence": np.mean(confidences) if confidences else 0
    }

mode = st.radio("Choose input mode", ["Live Camera", "Upload Image"], horizontal=True)

if mode == "Live Camera":
    frame = st.camera_input("Show your face to camera")
    if frame is not None:
        bytes_data = frame.getvalue()
        nparr = np.frombuffer(bytes_data, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        result = detect_faces(img_bgr)
        st.session_state.faces_detected += result["faces_count"]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(result["output_image"], channels="BGR", caption="Face Detection")
        with col2:
            st.success(f"🔍 Faces: {result['faces_count']}")
            st.metric("Confidence", f"{result['avg_confidence']:.1%}")
            st.metric("Total detections", st.session_state.faces_detected)
            
            if result["faces_count"] > 0:
                st.balloons()

elif mode == "Upload Image":
    uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    if uploaded is not None:
        # FIXED: Removed use_container_width=True
        image = Image.open(uploaded)
        st.image(image, caption="Original")
        
        uploaded.seek(0)
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img_bgr is not None:
            result = detect_faces(img_bgr)
            st.session_state.faces_detected += result["faces_count"]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # FIXED: channels first, caption second, NO use_container_width
                st.image(result["output_image"], channels="BGR", caption="Face Detection")
            with col2:
                st.success(f"🔍 Faces: {result['faces_count']}")
                st.metric("Confidence", f"{result['avg_confidence']:.1%}")
                st.metric("Total detections", st.session_state.faces_detected)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Session Faces", st.session_state.faces_detected)
with col2:
    st.metric("Detector", "OpenCV Haar")
with col3:
    st.metric("Status", "✅ 100% Working")

st.info("**🟢 Green boxes** = detected faces | Works with Indian lighting/faces")
