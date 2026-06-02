import streamlit as st
import os
import json
import plotly.io as pio

from graph import app 

st.set_page_config(page_title="Autonomous Data Analyst", layout="wide")

st.title("🧠 Zero-Prompt Autonomous Data Analyst")
st.markdown("Upload your sales data, and the multi-agent swarm will analyze, code, build charts, and report.")

UPLOAD_DIR = "Data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload a CSV file to begin", type=["csv"])

if uploaded_file is not None:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name).replace("\\", "/")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"Dataset securely staged at `{file_path}`. Ready for swarm ingestion.")
    if st.button("🚀 Initialize Swarm", type="primary", width="stretch"):
        with st.spinner("Swarm initialized. Orchestrating agents... This may take a minute."):
            initial_state = {
                "file_path": file_path,
                "error_logs": [],
                "current_exec_status": ""
            }
            final_state = app.invoke(initial_state, config={"configurable": {"thread_id": "1"}, "recursion_limit": 15})
            
            st.markdown("---")
            st.markdown("### 📊 Visual Analytics Dashboard")
            figures_json = final_state.get("figures", [])
            
            if figures_json:
                cols = st.columns(2)
                for i, fig_json in enumerate(figures_json):
                    fig = pio.from_json(fig_json)
                    with cols[i % 2]:
                        st.plotly_chart(fig, width="stretch")
            else:
                st.info("No charts were generated for this dataset.")
                        
            st.markdown("---")
            report = final_state.get("final_report", "No report generated.")
            st.markdown(report)
            st.download_button(
                label="📥 Download Full Report (Markdown)",
                data=report,
                file_name="Executive_Report.md",
                mime="text/markdown",
                width="stretch"
            )
            
            st.markdown("---")
            st.markdown("### ⚡ Real-World Automations")
            
            anomalies = final_state.get("anomalies", [])
            at_risk = final_state.get("at_risk_customers", []) 
            st.success(f"Sent {len(anomalies)} anomalies and {len(at_risk)} at-risk entities to Make.com.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚨 Anomalies Detected (Slack Webhook)")
                st.json(anomalies)                
            with col2:
                st.markdown("#### ⚠️ At-Risk Entities / Campaigns")
                st.json(at_risk)