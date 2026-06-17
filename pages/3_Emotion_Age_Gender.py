
import streamlit as st
import cv2
import numpy as np

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Age + Gender Detection", layout="wide")
st.title("Real-Time Age + Gender (Webcam + Image Upload)")

st.markdown(
    "This module uses a lightweight pretrained CNN to **estimate** age range and "
    "gender from face images. Predictions are approximate and may be biased."
)

# ---------- MODEL PATHS ----------
FACE_PROTO = "models/deploy.prototxt.txt"
FACE_MODEL = "models/res10_300x300_ssd_iter_140000.caffemodel"

AGE_PROTO = "models/age_deploy.prototxt"
AGE_MODEL = "models/age_net.caffemodel"

GENDER_PROTO = "models/gender_deploy.prototxt"
GENDER_MODEL = "models/gender_net.caffemodel"

AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
            '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

# ---------- LOAD MODELS ----------
@st.cache_resource
def load_models():
    face_net = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)
    age_net = cv2.dnn.readNetFromCaffe(AGE_PROTO, AGE_MODEL)
    gender_net = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)
    return face_net, age_net, gender_net

try:
    face_net, age_net, gender_net = load_models()
except Exception as e:
    st.error(
        "❌ Model load error.\n"
        "Check that `models/` folder contains:\n"
        "- deploy.prototxt\n"
        "- res10_300x300_ssd_iter_140000.caffemodel\n"
        "- age_deploy.prototxt, age_net.caffemodel\n"
        "- gender_deploy.prototxt, gender_net.caffemodel\n\n"
        f"Details: {e}"
    )
    st.stop()


# ---------- HELPERS ----------
def detect_faces_dnn(frame, conf_threshold=0.6):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        frame, 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False
    )
    face_net.setInput(blob)
    detections = face_net.forward()
    boxes = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype("int")
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)
            boxes.append((x1, y1, x2, y2))
    return boxes


def predict_age_gender(face_img):
    blob = cv2.dnn.blobFromImage(
        image=face_img,
        scalefactor=1.0,
        size=(227, 227),
        mean=MODEL_MEAN_VALUES,
        swapRB=False,
    )
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]

    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = AGE_LIST[age_preds[0].argmax()]

    return age, gender


def process_frame(frame_bgr, frame_width=640, conf_thr=0.6):
    """Resize frame, detect faces, draw boxes + labels, return output image."""
    if frame_bgr is None:
        return None

    h0, w0 = frame_bgr.shape[:2]
    scale = frame_width / float(w0)
    frame = cv2.resize(frame_bgr, None, fx=scale, fy=scale)
    output = frame.copy()

    boxes = detect_faces_dnn(frame, conf_threshold=conf_thr)

    for (x1, y1, x2, y2) in boxes:
        face = frame[y1:y2, x1:x2]
        if face.size == 0:
            continue

        age, gender = predict_age_gender(face)

        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        y_text = y1 - 10 if y1 - 10 > 20 else y1 + 20

        cv2.putText(
            output, f"Gender (est.): {gender}",
            (x1, y_text),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
        )
        cv2.putText(
            output, f"Age (est.): {age}",
            (x1, y_text + 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
        )

    return output


# ---------- UI ----------
st.sidebar.markdown("### Settings")
resize_width = st.sidebar.slider("Frame width", 320, 960, 640, step=80)
conf_thr = st.sidebar.slider("Face confidence threshold", 0.4, 0.9, 0.6, step=0.05)

col_cam, col_upload = st.columns(2)

with col_cam:
    st.subheader("Webcam")
    cam_image = st.camera_input("Capture from camera")

with col_upload:
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader(
        "Upload a face image (jpg/png)", type=["jpg", "jpeg", "png"]
    )

st.markdown("---")

# ---------- PROCESS CAMERA ----------
if cam_image is not None:
    file_bytes = np.asarray(bytearray(cam_image.getvalue()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    result = process_frame(frame, frame_width=resize_width, conf_thr=conf_thr)
    if result is not None:
        st.image(
    result, channels="BGR",
    caption="Webcam: Estimated Age & Gender"
)

        

# ---------- PROCESS UPLOADED IMAGE ----------
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    result = process_frame(img, frame_width=resize_width, conf_thr=conf_thr)
    if result is not None:
        # st.image(
        #     result, channels="BGR",
        #     caption="Uploaded Image: Estimated Age & Gender",
        #     use_container_width=True,
        # )
        st.image(result, channels="BGR", caption="Uploaded Image: Estimated Age & Gender")
