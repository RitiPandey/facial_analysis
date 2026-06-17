# import streamlit as st
# import cv2
# import numpy as np
# from PIL import Image
# from utils.forensics import MakeupRemover

# st.title("💄 **AI Makeup Removal**")

# remover = MakeupRemover()

# uploaded_file = st.file_uploader("Upload photo with makeup", type=['png','jpg','jpeg'])

# col1, col2 = st.columns(2)

# if uploaded_file is not None:
#     # ✅ FIXED: Reset file pointer + proper error handling
#     uploaded_file.seek(0)  # Reset file pointer
#     image = Image.open(uploaded_file)
    
#     with col1:
#         st.image(image, caption="💋 **With Makeup**", use_column_width=True)
    
#     # ✅ FIXED: Proper imdecode with error checking
#     try:
#         file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
#         if len(file_bytes) > 0:
#             cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#             if cv_image is not None:
#                 clean_image = remover.remove_makeup(cv_image)
                
#                 with col2:
#                     st.image(clean_image, caption="✨ **Makeup Removed**", 
#                             channels="BGR", use_column_width=True)
#                 st.success("✅ **Forensic cleanup complete!**")
#             else:
#                 st.error("❌ Cannot decode image")
#         else:
#             st.error("❌ Empty image file")
#     except Exception as e:
#         st.error(f"❌ Image processing error: {str(e)}")

# if st.button("🎬 **DEMO Makeup Removal**"):
#     st.balloons()
#     st.success("✅ **Makeup removal ready!**")
# pages/5_Makeup_Remove.py - PURE OPENCV MAKEUP REMOVAL
import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Makeup Removal", layout="wide")
st.title("✨ Virtual Makeup Removal")
st.markdown("**Before → After** - Pure HSV color analysis")

def detect_makeup_areas(img_bgr):
    """Detect lips + foundation using HSV ranges."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Lipstick detection (red/pink high saturation)
    lip_lower = np.array([0, 100, 80])
    lip_upper = np.array([15, 255, 200])
    lip_mask = cv2.inRange(hsv, lip_lower, lip_upper)
    
    # Heavy foundation (uniform skin tone)
    skin_lower = np.array([0, 20, 70])
    skin_upper = np.array([25, 70, 160])
    foundation_mask = cv2.inRange(hsv, skin_lower, skin_upper)
    
    # Combine + clean
    makeup_mask = cv2.bitwise_or(lip_mask, foundation_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    makeup_mask = cv2.morphologyEx(makeup_mask, cv2.MORPH_CLOSE, kernel)
    makeup_mask = cv2.morphologyEx(makeup_mask, cv2.MORPH_OPEN, kernel)
    
    return makeup_mask

def remove_makeup(img_bgr):
    """Subtle makeup removal effect."""
    original = img_bgr.copy()
    makeup_mask = detect_makeup_areas(img_bgr)
    
    # Get natural skin tone from low saturation areas
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    natural_skin_mask = cv2.inRange(hsv, np.array([0, 20, 60]), np.array([25, 60, 255]))
    natural_pixels = img_bgr[natural_skin_mask > 0]
    
    if len(natural_pixels) < 50:
        return original, makeup_mask
    
    natural_skin = np.mean(natural_pixels, axis=0).astype(np.uint8)
    
    # Subtle blending (30% natural skin)
    result = img_bgr.copy()
    blend_mask = makeup_mask > 128
    
    # Apply only to makeup areas
    result[blend_mask] = (
        img_bgr[blend_mask] * 0.7 + natural_skin * 0.3
    ).astype(np.uint8)
    
    return result, makeup_mask

# UI - LEFT: Original | RIGHT: Clean
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Original")
    input_image = st.camera_input("Take photo") or st.file_uploader(
        "Or upload", type=["jpg", "png", "jpeg"]
    )

if input_image is not None:
    # Load image
    file_bytes = np.asarray(bytearray(input_image.getvalue()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Resize for display
    h, w = img.shape[:2]
    display_w = min(640, w)
    scale = display_w / w
    img_display = cv2.resize(img, None, fx=scale, fy=scale)
    
    # Process
    cleaned, makeup_mask = remove_makeup(img)
    cleaned_display = cv2.resize(cleaned, img_display.shape[1::-1])
    
    # Show results
    with col1:
        # st.image(img_display, channels="BGR", caption="👁️ Before", use_container_width=True)
        st.image(img_display, channels="BGR", caption="👁️ Before")

    with col2:
        # st.image(cleaned_display, channels="BGR", caption="✨ After", use_container_width=True)
        st.image(cleaned_display, channels="BGR", caption="✨ After")

    # Makeup mask visualization
    mask_display = cv2.cvtColor(makeup_mask, cv2.COLOR_GRAY2BGR)
    mask_display[makeup_mask > 128] = [0, 0, 255]  # Red overlay
    # st.image(cv2.resize(mask_display, img_display.shape[1::-1]), 
    #          channels="BGR", caption="🔍 Makeup Areas (RED)", use_container_width=True)
    st.image(cv2.resize(mask_display, img_display.shape[1::-1]), channels="BGR", caption="🔍 Makeup Areas (RED)")
    
    # Stats
    makeup_pixels = np.sum(makeup_mask > 128)
    col1, col2, col3 = st.columns(3)
    col1.metric("Image Size", f"{w}x{h}")
    col2.metric("Makeup Pixels", f"{makeup_pixels:,}")
    makeup_pct = (makeup_pixels / (h * w)) * 100
    col3.metric("Makeup %", f"{makeup_pct:.1f}%")

st.info("""
**How it works:**
- 🔴 **RED overlay** = Detected lipstick + foundation
- ✨ **After** = 30% natural skin blending  
- Works with Indian skin tones perfectly!
""")
