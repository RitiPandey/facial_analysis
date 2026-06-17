# # pages/6_emotion.py
# import streamlit as st
# from modules.emotion import run_emotion_detection

# st.title("😀 Emotion Detection Module")
# st.markdown("**Module 6/9 - Live Emotion Recognition**")

# # Call backend
# run_emotion_detection()

# st.success("✅ Emotion module working perfectly!")
# st.balloons()
# pages/6_emotion.py
# pages/6_emotion.py
import streamlit as st
from modules.emotion import run_emotion_detection


st.set_page_config(page_title="Emotion Detection", page_icon="😀", layout="wide")
run_emotion_detection()
