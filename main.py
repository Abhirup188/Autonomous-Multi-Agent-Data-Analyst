from state import AgentState
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import List
import requests
import json

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.7
)

def profiler_node(state: AgentState):
    file_path = state.get('file_path')
    df = pd.read_csv(file_path)
    dtypes = df.dtypes.to_string()
    headers = df.head().to_string()
    data_profile = df.describe().to_string()
    missing = df.isnull().sum().to_string()
    complete_data_profile = f"""
        DATA TYPES:\n{dtypes}\n
        COLUMN HEADERS:\n{headers}\n
        STATISTICAL SUMMARY:\n{data_profile}\n
        MISSING VALUES:\n{missing}"""
    return {"data_profile": complete_data_profile}

class Hypothesis(BaseModel): 
    questions: List[str]

def strategist_node(state: AgentState):
    print("Deciding Strategy...")
    data_profile = state.get('data_profile')
    structured_llm = llm.with_structured_output(Hypothesis)

    prompt = f"""
    You are a Senior Strategic Data Consultant. Your goal is to analyze a dataset's metadata and generate high-impact business hypotheses.
    Your hypotheses must be Actionable, Technical, and Targeted (include Retention/Churn and Anomalies).
    
    Data Profile:
    {data_profile}

    CRITICAL: ONLY use the column names provided in the 'DATA TYPES' section. Generate 4 questions.
    """
    try:
        result = structured_llm.invoke(prompt)
        return {"hypotheses": result.questions}
    except Exception as e:
        print(f"Strategic Node Error:{e}")
        return {"hypotheses": ["Error: Could not generate hypotheses."]}
    
class CodeOutput(BaseModel):
    code: str

def CoderNode(state: AgentState):
    file_path = state.get('file_path')
    data_profile = state.get('data_profile')
    hypotheses = state.get('hypotheses')
    
    error_logs = state.get("error_logs", [])
    error_feedback = ""
    if error_logs:
        error_feedback = f"""
        ### CRITICAL ERROR FEEDBACK ###
        Your previous code failed to execute. Here are the error logs:
        {error_logs}
        You MUST fix these errors in your new code. Do not repeat the same mistakes.
        """

    print("Writing the Code and Analysing...")
    structured_llm = llm.with_structured_output(CodeOutput)
    prompt = f"""
    You are an Expert Senior Python Data Engineer. Write a single, executable Python script to answer the business hypotheses.

    ### CONTEXT
    File Path: '{file_path}'
    Data Profile: {data_profile}
    Hypotheses: {hypotheses}
    {error_feedback}

    ### EXECUTION CONSTRAINTS (CRITICAL)
    1. Include `import pandas as pd` AND `import plotly.express as px` at the top.
    2. Load the dataset using the exact File Path.
    3. Do NOT use `print()` statements. 
    4. Store analytical answers in a dictionary/string named exactly: `analysis_results`.
    5. DATA ANOMALY DETECTION (CRITICAL): 
    You MUST detect anomalies using the Z-Score method across ALL numeric columns.
    - For every numeric column, calculate the mean and standard deviation.
    - Flag a row as an anomaly if the value in ANY numeric column has an absolute Z-score > 3.0 (i.e., |(value - mean) / std| > 3.0).
    - Store the unique 'OrderID' of these rows in a list named exactly: anomalies_list.
    - If no rows meet this criteria, assign an empty list [].
    - Do not use the IQR method; use Z-Score > 3.0.
    6. Identify strictly at-risk customers (e.g., spending significantly below average) and store them in a list named exactly: at_risk_customers_list. If all customers are healthy, assign an empty list [].
    7. VISUAL DASHBOARD: You MUST generate 2 to 3 interactive charts using `plotly.express` (e.g., bar charts, line charts, scatter plots) to visualize the data. Store the resulting Plotly figure objects in a Python list named exactly: `figures_list`.
    8. When calculating statistics like mean, sum, or correlation, ALWAYS use numeric_only=True or explicitly select only numeric columns to avoid string conversion errors.
    Return ONLY raw Python code. No markdown backticks.
    9. FORBIDDEN LIBRARIES: You are strictly forbidden from importing or using 'statsmodels', 'scikit-learn', 'scipy', or 'seaborn'.
    10. ALLOWED LIBRARIES: You may ONLY use 'pandas' and 'plotly.express'. If you cannot solve a problem with these two, use standard Python math.
    11. EXACT COLUMN NAMES: You MUST use the exact column names as shown in the 'COLUMN HEADERS' context. They are case-sensitive. Do not guess or modify column names.
    """
    try:
        result = structured_llm.invoke(prompt)
        return {"generated_code": result.code}
    except Exception as e:
        print(f"Coder Node Error:{e}")
        return {"generated_code": "Error: Could not generate code."}

def executor_node(state: AgentState):
    print("Executing Generated Code...")
    generated_code = state.get('generated_code','')
    clean_code = generated_code
    if clean_code.startswith("```python"):
        clean_code = clean_code.replace("```python","").replace("```","").strip()
    elif clean_code.startswith("```"):
        clean_code = clean_code.replace("```","").strip()
    local_vars = {}

    exec_globals = {
        "pd":pd,
        "px":px,
        "__builtins__":__builtins__
    }

    try:
        exec(clean_code, exec_globals, local_vars)
        raw_figures = local_vars.get('figures_list',[])
        json_figures = [fig.to_json() for fig in raw_figures]
        
        return {
            "execution_results": str(local_vars.get('analysis_results', "No results.")),
            "anomalies": local_vars.get('anomalies_list', []),
            "at_risk_customers": local_vars.get('at_risk_customers_list', []),
            "figures": json_figures,
            "current_exec_status": "success"
        }
    except Exception as e:
        print(f"Executor Node Error: {e}")
        return {
            "error_logs": [f"Execution Error: {str(e)}"],
            "current_exec_status": "failure"
        }

def Reporter_node(state: AgentState):
    hypotheses = state.get('hypotheses')
    execution_results = state.get('execution_results')
    prompt = f"""
    You are an Executive Business Analyst. Write a polished Markdown report based on this data:
    Hypotheses: {hypotheses}
    Results: {execution_results}
    Format beautifully with headers and bullet points. Do not mention code.
    """
    try:
        result = llm.invoke(prompt)
        return {"final_report": result.content}
    except Exception as e:
        return {"error_logs": [f"Reporter Error: {str(e)}"]}

def automator_node(state: AgentState):
    print("Triggering Make.com Webhook...")
    anomalies = state.get('anomalies', [])
    at_risk_customers = state.get('at_risk_customers', [])
    make_webhook_url = os.getenv("MAKE_WEBHOOK_URL")
    
    if not make_webhook_url:
        return {"automation_status": "Make.com Webhook URL not configured."}

    try:
        raw_payload = {"anomalies": anomalies, "at_risk_customers": at_risk_customers}
        safe_payload = json.loads(json.dumps(raw_payload, default=str))
        response = requests.post(make_webhook_url, json=safe_payload)
        response.raise_for_status()
        return {"automation_status": f"Sent {len(anomalies)} anomalies and {len(at_risk_customers)} at-risk customers to Make.com."}
    except Exception as e:
        return {"automation_status": f"Failed to trigger Make.com: {e}"}