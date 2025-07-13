import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📊 View Evaluation Logs", layout="wide")

st.title("📄 Logged Evaluations")

LOG_FILE = "logs/eamr_rag_eval.xlsx"

if os.path.exists(LOG_FILE):
    df = pd.read_excel(LOG_FILE)

    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    examiner_filter = st.sidebar.selectbox("Filter by Examiner", ["All"] + sorted(df["Examiner"].dropna().unique().tolist()))
    model_filter = st.sidebar.selectbox("Filter by Model", ["All"] + sorted(df["Model"].dropna().unique().tolist()))

    filtered_df = df.copy()
    if examiner_filter != "All":
        filtered_df = filtered_df[filtered_df["Examiner"] == examiner_filter]
    if model_filter != "All":
        filtered_df = filtered_df[filtered_df["Model"] == model_filter]

    st.dataframe(filtered_df, use_container_width=True)

    with st.expander("📥 Download Filtered Log as Excel"):
        st.download_button(
            label="Download Excel",
            data=filtered_df.to_excel(index=False, engine='openpyxl'),
            file_name="filtered_eamr_eval_log.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("🚫 Log file not found.")
