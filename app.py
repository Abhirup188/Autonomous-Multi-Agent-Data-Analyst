import streamlit as st
import os
import uuid
import plotly.io as pio
from graph import app as swarm_app

UPLOAD_DIR = "Data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Autonomous Data Analyst", layout="wide", page_icon="🤖")

st.title("🤖 Zero-Prompt Autonomous Data Analyst")
st.markdown("Upload your sales data, and the multi-agent swarm will analyze, code, build charts, and report.")
st.markdown("---")

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
                "data_profile": "",
                "hypotheses": [],
                "generated_code": "",
                "execution_results": "",
                "anomalies": [],
                "at_risk_customers": [],
                "final_report": "",
                "error_logs": [],
                "automation_status": "",
                "figures": [] 
            }

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            
            try:
                final_state = swarm_app.invoke(initial_state, config)

                if "Error" in final_state.get("generated_code", "") or (final_state.get("error_logs") and len(final_state.get("error_logs")) >= 3):
                    st.error("⚠️ The swarm encountered a critical error it could not self-heal.")
                    st.code("\n".join(final_state.get("error_logs", ["Unknown Execution Error"])), language="bash")
                    st.stop()

                st.balloons()

                st.markdown("### 📈 Visual Analytics Dashboard")
                st.info("Interactive charts dynamically coded and rendered by the Swarm.")
                figures_json = final_state.get("figures", [])
                
                if figures_json:
                    cols = st.columns(len(figures_json) if len(figures_json) <= 2 else 2)
                    for i, fig_json in enumerate(figures_json):
                        # Rebuild the Plotly figure from the JSON string
                        fig = pio.from_json(fig_json) 
                        with cols[i % 2]:
                            st.plotly_chart(fig, width="stretch")
                else:
                    st.warning("No visual charts were generated for this dataset.")

                st.markdown("---")
                
                st.markdown("### 📊 Executive Report")
                report_content = final_state.get("final_report", "No report generated.")
                st.markdown(report_content)

                st.download_button(
                    label="📥 Download Full Report (Markdown)",
                    data=report_content,
                    file_name="AI_Executive_Report.md",
                    mime="text/markdown",
                    width="stretch"
                )
                
                st.markdown("---")

                st.markdown("### ⚡ Real-World Automations")
                st.success(final_state.get("automation_status", "No status available."))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🚨 Anomalies Detected (Slack Webhook)**")
                    st.write(final_state.get("anomalies", ["None"]))
                with col2:
                    st.markdown("**⚠️ At-Risk Customers (CRM Tagging)**")
                    st.write(final_state.get("at_risk_customers", ["None"]))

            except Exception as e:
                st.error(f"System Failure: {e}")