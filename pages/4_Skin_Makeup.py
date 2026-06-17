
# pages/4_Skin_Makeup.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Skin & Makeup Analysis", layout="wide")
st.title("🧴 Skin Type + Makeup Analysis + Face Detection")
st.markdown("**Skin type, makeup percentage, faces detected**")

@st.cache_resource
def load_cascades():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_cascades()

def analyze_skin_makeup(img_bgr):
    """Complete analysis: skin type, makeup %, faces."""
    h, w = img_bgr.shape[:2]
    
    # 1. FACE DETECTION (Green boxes)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
    face_count = len(faces)
    
    # 2. SKIN DETECTION (Tuned for Indian skin)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    skin_mask = cv2.inRange(hsv, np.array([0, 25, 60]), np.array([25, 170, 255]))
    
    # Clean skin mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
    
    skin_pixels_total = np.sum(skin_mask > 0)
    
    if skin_pixels_total < 500:
        return None
    
    # 3. SKIN TYPE ANALYSIS
    skin_pixels = img_bgr[skin_mask > 100]
    
    # Skin tone (LAB L channel)
    lab_skin = cv2.cvtColor(skin_pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2LAB)
    L_mean = np.mean(lab_skin[:,:,0])
    
    if L_mean < 85:
        skin_tone = "dark"
    elif L_mean < 125:
        skin_tone = "medium"
    else:
        skin_tone = "light"
    
    # Oiliness (HSV Saturation + Value variance)
    hsv_skin = cv2.cvtColor(skin_pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_BGR2HSV)
    s_var = np.var(hsv_skin[:,:,1])
    v_var = np.var(hsv_skin[:,:,2])
    
    if s_var + v_var > 2000:
        skin_type = "oily"
    elif s_var + v_var < 800:
        skin_type = "dry"
    else:
        skin_type = "normal"
    
    # 4. MAKEUP DETECTION
    # Heavy foundation: uniform color + high coverage
    color_std = np.std(skin_pixels, axis=0).mean()
    coverage_ratio = skin_pixels_total / (h * w)
    
    if color_std < 20 and coverage_ratio > 0.25:
        makeup_level = "heavy"
        makeup_pct = 75
    elif color_std < 30 or coverage_ratio > 0.35:
        makeup_level = "medium"
        makeup_pct = 45
    elif color_std < 40:
        makeup_level = "light"
        makeup_pct = 20
    else:
        makeup_level = "none"
        makeup_pct = 0
    
    # 5. VISUALIZATION
    output = img_bgr.copy()
    
    # Face boxes (GREEN)
    for i, (x, y, fx, fy) in enumerate(faces):
        cv2.rectangle(output, (x, y), (x+fx, y+fy), (0, 255, 0), 3)
        cv2.putText(output, f"Face {i+1}", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Skin overlay (LIGHT BLUE)
    output[skin_mask > 128] = output[skin_mask > 128] * 0.7 + np.array([200, 230, 255]) * 0.3
    output[skin_mask > 128] = np.clip(output[skin_mask > 128], 0, 255).astype(np.uint8)
    
    # Labels
    y_pos = 30
    labels = [
        f"Faces: {face_count}",
        f"Skin Type: {skin_type} ({skin_tone} tone)",
        f"Makeup: {makeup_level} ({makeup_pct}%)",
        f"Skin pixels: {skin_pixels_total:,}"
    ]
    
    for label in labels:
        cv2.putText(output, label, (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        y_pos += 40
    
    return {
        "output_image": output,
        "face_count": face_count,
        "skin_type": skin_type,
        "skin_tone": skin_tone,
        "makeup_level": makeup_level,
        "makeup_pct": makeup_pct,
        "skin_pixels": skin_pixels_total
    }

# UI
col1, col2 = st.columns(2)
with col1:
    st.subheader("📷 Camera")
    cam_img = st.camera_input("Take photo")
with col2:
    st.subheader("⬆️ Upload")
    upload_img = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

def process_image(img_file):
    file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img.shape[1] > 640:
        scale = 640 / img.shape[1]
        img = cv2.resize(img, None, fx=scale, fy=scale)
    
    return analyze_skin_makeup(img)

# Process Camera
if cam_img:
    result = process_image(cam_img)
    if result:
        # st.image(result["output_image"], channels="BGR", caption="✅ Camera Analysis", use_container_width=True)
        st.image(result["output_image"], channels="BGR", caption="✅ Camera Analysis")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Faces", result["face_count"])
        col2.metric("Skin Type", f"{result['skin_type'].title()} ({result['skin_tone']})")
        col3.metric("Makeup", f"{result['makeup_pct']}%")
        col4.metric("Skin Area", f"{result['skin_pixels']:,}")

# Process Upload
if upload_img:
    result = process_image(upload_img)
    if result:
        # st.image(result["output_image"], channels="BGR", caption="✅ Upload Analysis", use_container_width=True)
        st.image(result["output_image"], channels="BGR", caption="✅ Upload Analysis")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Faces", result["face_count"])
        col2.metric("Skin Type", f"{result['skin_type'].title()} ({result['skin_tone']})")
        col3.metric("Makeup", f"{result['makeup_pct']}%")
        col4.metric("Skin Area", f"{result['skin_pixels']:,}")

# Legend
st.markdown("---")
st.subheader("📊 Analysis Guide")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **🟢 Green Box** = Face detected
    **🔵 Light Blue** = Skin detected
    """)
with col2:
    st.markdown("""
    **Skin Types:**
    - Oily: High shine/variance
    - Dry: Low texture/color
    - Normal: Balanced
    """)
with col3:
    st.markdown("""
    **Makeup Levels:**
    - 0% = Natural
    - 20% = Light
    - 45% = Medium  
    - 75% = Heavy
    """)

st.success("✅ **Complete Analysis**: Faces + Skin Type + Makeup %")
