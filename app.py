import streamlit as st
import os
import json
import plotly.io as pio

# Import your compiled LangGraph workflow
from graph import app 

st.set_page_config(page_title="Autonomous Data Analyst", layout="wide")

st.title("🧠 Zero-Prompt Autonomous Data Analyst")
st.markdown("Upload your sales data, and the multi-agent swarm will analyze, code, build charts, and report.")

# Ensure the upload directory exists
UPLOAD_DIR = "Data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload a CSV file to begin", type=["csv"])

if uploaded_file is not None:
    # PATCH 1: Windows Filepath Bug Fix (forcing forward slashes)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name).replace("\\", "/")
    
    # Save the file locally so the Swarm can read it
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"Dataset securely staged at `{file_path}`. Ready for swarm ingestion.")
    
    # PATCH 2: Streamlit UI Deprecation Fix (width="stretch")
    if st.button("🚀 Initialize Swarm", type="primary", width="stretch"):
        with st.spinner("Swarm initialized. Orchestrating agents... This may take a minute."):
            
            # 1. Setup the initial state payload for LangGraph
            initial_state = {
                "file_path": file_path,
                "error_logs": [],
                "current_exec_status": ""
            }
            
            # 2. Execute the Swarm
            final_state = app.invoke(initial_state, config={"configurable": {"thread_id": "1"}, "recursion_limit": 15})
            
            st.markdown("---")
            
            # --- RENDER DASHBOARD ---
            st.markdown("### 📊 Visual Analytics Dashboard")
            figures_json = final_state.get("figures", [])
            
            if figures_json:
                cols = st.columns(2)
                for i, fig_json in enumerate(figures_json):
                    fig = pio.from_json(fig_json)
                    with cols[i % 2]:
                        # PATCH 2: Streamlit UI Deprecation Fix
                        st.plotly_chart(fig, width="stretch")
            else:
                st.info("No charts were generated for this dataset.")
                        
            st.markdown("---")
            
            # --- RENDER EXECUTIVE REPORT ---
            report = final_state.get("final_report", "No report generated.")
            st.markdown(report)
            
            # PATCH 2: Streamlit UI Deprecation Fix
            st.download_button(
                label="📥 Download Full Report (Markdown)",
                data=report,
                file_name="Executive_Report.md",
                mime="text/markdown",
                width="stretch"
            )
            
            st.markdown("---")
            
            # --- RENDER REAL-WORLD AUTOMATIONS ---
            st.markdown("### ⚡ Real-World Automations")
            
            anomalies = final_state.get("anomalies", [])
            
            # Note: The backend state variable remains 'at_risk_customers' for graph logic compatibility, 
            # but we present it as 'entities' on the frontend to avoid hallucinated marketing contexts.
            at_risk = final_state.get("at_risk_customers", []) 
            
            # PATCH 3: The "At-Risk Entities" UI Fix
            st.success(f"Sent {len(anomalies)} anomalies and {len(at_risk)} at-risk entities to Make.com.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚨 Anomalies Detected (Slack Webhook)")
                st.json(anomalies)
                
            with col2:
                # PATCH 3: Re-labeled to natively support Ad Campaigns & non-customer entities
                st.markdown("#### ⚠️ At-Risk Entities / Campaigns")
                st.json(at_risk)