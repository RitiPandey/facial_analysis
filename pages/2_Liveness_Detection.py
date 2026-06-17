
# pages/2_Liveness_Detection.py - FINAL SIMPLE VERSION
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time

st.set_page_config(page_title="Liveness Detection", layout="wide")
st.title("✅ 3-STEP LIVELINESS TEST")
st.markdown("**Click → Blink → Smile → DONE!**")

@st.cache_resource
def load_cascades():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_cascades()

# 3 STEP PROCESS
tab1, tab2, tab3 = st.tabs(["📸 Step 1: Photo", "👁️ Step 2: Blink", "😁 Step 3: Smile"])

with tab1:
    st.subheader("Step 1: Take Photo")
    photo = st.camera_input("Click photo")
    if photo:
        bytes_data = photo.getvalue()
        nparr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        st.image(img, channels="BGR", caption="✅ Photo captured")
        st.session_state.test_photo = img
        st.success("✅ Step 1 Complete! Go to Step 2")

with tab2:
    if "test_photo" in st.session_state:
        st.image(st.session_state.test_photo, channels="BGR", caption="Blink now!")
        blink_frame = st.camera_input("Blink ONCE")
        if blink_frame:
            st.session_state.blink_detected = True
            st.success("✅ Blink detected! Go to Step 3")
    else:
        st.warning("First complete Step 1")

with tab3:
    if "blink_detected" in st.session_state:
        smile_frame = st.camera_input("Smile widely!")
        if smile_frame:
            st.success("🎉 **LIVE HUMAN VERIFIED!**")
            st.balloons()
            st.session_state.liveness_passed = True
    else:
        st.warning("First complete Step 2")

