import streamlit as st
import requests
import pandas as pd
import os
import io
from datetime import datetime
from github import Github
from io import BytesIO

st.set_page_config(page_title="🧬 eAMR RAG Evaluator", layout="wide")
st.title("🧪 eAMR RAG Evaluation Interface")

# 📁 Ensure logs directory exists
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/eamr_rag_eval.xlsx"
def reset_session():
    keys_to_clear = [
        "relevance", "relevance_comment",
        "factual", "factual_comment",
        "response_time", "response_comment",
        "perspective", "perspective_comment",
        "general_comment",
        "query_ran", "data", "query", "model_choice", "examiner", "n_results"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
# 🔄 Reset button
if st.sidebar.button("🔄 Reset App"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Sidebar settings
st.sidebar.header("🛠️ Settings")
view_mode = st.sidebar.radio("Mode", ["📝 Evaluate", "📑 View Logs"])

if view_mode == "📑 View Logs":
    
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
            towrite = io.BytesIO()
            filtered_df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)  # reset pointer to start

            st.download_button(
                label="Download Excel",
                data=towrite,
                file_name="filtered_eamr_eval_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("🚫 Log file not found.")

else:
    model_choice = st.sidebar.radio("Select RAG Model", ["Gemini", "LLaMA"])
    n_results = st.sidebar.slider("Number of documents to retrieve", 1, 10, 5)
    examiner = st.sidebar.text_input("Examiner Name", value="")

    API_ENDPOINTS = {
        "Gemini": "http://196.190.220.63:8000/api/pipeline/gemini",
        "LLaMA": "http://196.190.220.63:8000/api/pipeline/llama"
    }

    # Query input
    st.subheader("🔍 Ask a Question")
    query = st.text_area("Enter your query", height=100)

    # Initialize flags
    if "query_ran" not in st.session_state:
        st.session_state.query_ran = False

    # Run Query button
    if st.button("🔎 Run Query"):
        if not query.strip() or not examiner.strip():
            st.warning("Please provide both a query and examiner name.")
        else:
            st.session_state.query_ran = True
            with st.spinner("⏳ Running query..."):
                try:
                    payload = {"query": query, "n_result": n_results}
                    response = requests.post(API_ENDPOINTS[model_choice], json=payload)
                    response.raise_for_status()
                    st.session_state.data = response.json()
                    st.session_state.query = query
                    st.session_state.examiner = examiner
                    st.session_state.model_choice = model_choice
                    st.session_state.n_results = n_results
                except Exception as e:
                    st.error(f"❌ Failed to get response: {e}")
                    st.stop()

    # Show results if query ran
    if st.session_state.query_ran:
        data = st.session_state.data
        summary = data.get("summary", "No summary provided.")
        docs = data.get("documents", [])

        st.success("✅ Summary Generated!")
        st.markdown("### 📝 Summary")
        st.markdown(summary)

        st.markdown("### 📄 Retrieved Documents")
        for i, doc_group in enumerate(docs, 1):
            with st.expander(f"Document {i}"):
                for doc in doc_group:
                    st.markdown(doc)

        # Evaluation form
        st.markdown("### 📊 Evaluation Metrics")

        # Initialize evaluation keys
        default_state = {
            "relevance": 5,
            "relevance_comment": "",
            "factual": 5,
            "factual_comment": "",
            "response_time": 5,
            "response_comment": "",
            "perspective": 5,
            "perspective_comment": "",
            "general_comment": "",
        }

        for key, val in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = val

        col1, col2 = st.columns(2)

        with col1:
            st.slider("Relevance (1–10)", 1, 10, key="relevance")
            st.text_area("🗨️ Relevance Comment", key="relevance_comment")

            st.slider("Factual Accuracy (1–10)", 1, 10, key="factual")
            st.text_area("🗨️ Factual Accuracy Comment", key="factual_comment")

        with col2:
            st.slider("Response Time (1–10)", 1, 10, key="response_time")
            st.text_area("🗨️ Response Time Comment", key="response_comment")

            st.slider("Perspective Coverage (1–10)", 1, 10, key="perspective")
            st.text_area("🗨️ Perspective Coverage Comment", key="perspective_comment")

        st.text_area("💬 Overall Comments (Optional)", key="general_comment")

        if st.button("💾 Submit Evaluation"):
            log_data = {
                "Timestamp": datetime.now(),
                "Examiner": st.session_state.examiner,
                "Model": st.session_state.model_choice,
                "Query": st.session_state.query,
                "N_Results": st.session_state.n_results,
                "Summary": summary,
                "Documents": "\n".join([doc for group in docs for doc in group]),
                "Relevance": st.session_state.relevance,
                "Relevance_Comment": st.session_state.relevance_comment,
                "Factual_Accuracy": st.session_state.factual,
                "Factual_Accuracy_Comment": st.session_state.factual_comment,
                "Response_Time": st.session_state.response_time,
                "Response_Time_Comment": st.session_state.response_comment,
                "Perspective_Coverage": st.session_state.perspective,
                "Perspective_Comment": st.session_state.perspective_comment,
                "General_Comment": st.session_state.general_comment,
            }
            # Read existing log file from GitHub
            g = Github(st.secrets["github"]["token"])
            repo = g.get_user(st.secrets["github"]["repo_owner"]).get_repo(st.secrets["github"]["repo_name"])
            try:
                contents = repo.get_contents("logs/eamr_rag_eval.xlsx", ref=st.secrets["github"]["branch"])
                existing_file = BytesIO(contents.decoded_content)
                df_existing = pd.read_excel(existing_file)
            except:
                df_existing = pd.DataFrame(columns=list(log_data.keys()))

            # Append new row
            df_new = pd.concat([df_existing, pd.DataFrame([log_data])], ignore_index=True)

            # Save back to GitHub
            output = BytesIO()
            df_new.to_excel(output, index=False)
            output.seek(0)
            repo.update_file(
                path="logs/eamr_rag_eval.xlsx",
                message=f"Add new evaluation by {st.session_state.examiner}",
                content=output.read(),
                sha=contents.sha if 'contents' in locals() else None,
                branch=st.secrets["github"]["branch"]
            )

            st.success("✅ Evaluation logged successfully to GitHub!")
            reset_session()