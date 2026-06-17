import streamlit as st
import pandas as pd

st.title("📊 Accuracy Dashboard")

# Manual results enter karo (APNE ACTUAL NUMBERS DAALO)
data = {
    'Module': ['Face Detection', 'Gender', 'Age', 'Skin Analysis', 'Makeup Detection'],
    'Tests': [10, 10, 10, 10, 10],
    'Correct': [9, 8, 6, 7, 8]  # YE APNE ACTUAL TESTS KE HISAB SE CHANGE KARO
}

df = pd.DataFrame(data)
df['Accuracy'] = (df['Correct']/df['Tests']*100).round(1)

st.markdown("### 📈 Test Results")
st.dataframe(df, use_container_width=True)

overall = df['Accuracy'].mean()
st.metric("🎯 OVERALL PROJECT ACCURACY", f"{overall:.1f}%")

st.markdown("---")
st.success("""
**✅ VALIDATION METHOD:**
- 10 test images per module
- Indian faces + local lighting  
- Manual ground truth validation
- Professional accuracy testing!
""")

col1, col2, col3 = st.columns(3)
col1.metric("Total Tests", "50")
col2.metric("Correct Predictions", f"{df['Correct'].sum()}")
col3.metric("Project Score", f"{overall:.1f}%")
