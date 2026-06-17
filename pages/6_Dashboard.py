# pages/6_Dashboard.py - FULL ANALYTICS
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Complete Analytics Dashboard")

# Mock data (replace with real DB later)
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = []

# Generate demo data
def generate_demo_data():
    return pd.DataFrame({
        "timestamp": pd.date_range(start="2026-02-01", periods=50, freq="H"),
        "page": np.random.choice(["Face", "Liveness", "AgeGender", "Skin", "Makeup"], 50),
        "faces_detected": np.random.randint(1, 3, 50),
        "confidence": np.random.uniform(0.7, 0.99, 50),
        "skin_type": np.random.choice(["Oily", "Dry", "Normal"], 50),
        "makeup_pct": np.random.randint(0, 80, 50),
        "liveness": np.random.choice(["PASS", "FAIL"], 50)
    })

df = generate_demo_data()

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tests", len(df), 12)
col2.metric("Live Users", len(df[df.liveness=="PASS"]), 8)
col3.metric("Avg Confidence", f"{df.confidence.mean():.1%}", "0.5%")
col4.metric("Most Common Skin", df.skin_type.mode()[0])

# Charts
col1, col2 = st.columns(2)
with col1:
    st.subheader("Tests per Page")
    page_counts = df.page.value_counts()
    st.bar_chart(page_counts)

with col2:
    st.subheader("Liveness Success Rate")
    st.metric("Success", f"{(df.liveness=='PASS').mean():.1%}")

# Recent activity
st.subheader("Recent Activity")
recent = df.tail(10)[["timestamp", "page", "faces_detected", "liveness"]]
st.dataframe(recent)


