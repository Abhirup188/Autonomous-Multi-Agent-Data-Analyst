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
    model="gpt-4o",
    api_key=OPENAI_API_KEY,
    temperature=0.2
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
    
    5. DATA ANOMALY DETECTION (BUSINESS LOGIC): 
    - IGNORE individual item quantity fluctuations (e.g., ignore if a customer buys 2 units instead of 1).
    - YOU MUST DETECT ANOMALIES BASED ON BUSINESS RISK:
      a) AOV DROP: Calculate the mean 'Total Price Usd' per 'Gateway'. Flag any gateway where the AOV drops >30% compared to the overall mean.
      b) TAX DISCREPANCIES: Calculate the ratio of 'Total Tax' to 'Total Price Usd'. Flag any transaction where this ratio deviates more than 5% from the global median tax ratio (e.g., potential tax calculation error).
      c) MARKET OUTLIERS: Flag any orders where the 'Billing Address Country' is not 'United States' (if US is the target market).
    - CRITICAL: For each anomaly, output a clear string (e.g., "AOV ALERT: PayPal gateway AOV dropped 35% below mean").
    - CRITICAL: Limit to the TOP 5 most critical anomalies. Store in `anomalies_list`.

    6. "AT-RISK" ENTITY DETECTION (DYNAMIC):
    - Identify entities that are performing poorly based on the context of the data. If the dataset lacks 'Customers', evaluate campaigns, products, or regions.
    - CRITICAL: You must limit your output to ONLY the TOP 5 worst-performing entities. Store descriptive strings in a list named exactly: at_risk_customers_list. Assign [] if none exist.
    
    7. VISUAL DASHBOARD: Generate 3 interactive Business Intelligence charts using plotly.express (e.g., Stacked Bar charts, Pie charts, Line graphs).
    - CRITICAL: Do NOT generate academic statistical plots like Box Plots, Violin Plots, or Histograms. 
    - CRITICAL: If you create a time-series line chart, you MUST aggregate (groupby) the data by date and sort it chronologically BEFORE plotting to prevent overlapping "spaghetti" lines.
    - Store the Plotly figure objects in a list named exactly: figures_list.
    
    8. ALWAYS use numeric_only=True or explicitly select numeric columns for math.
    9. Return ONLY raw Python code. No markdown backticks.
    10. STRICTLY FORBIDDEN LIBRARIES: You will crash the system if you import 'scipy', 'statsmodels', 'sklearn', or 'seaborn'. Use ONLY standard Pandas and math.
    11. EXACT COLUMN NAMES: You MUST use the exact column names as shown in the 'COLUMN HEADERS'. Do not guess.
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
    You are an elite Executive Business Analyst. Write a polished, hardcore data-driven Markdown report based strictly on the following data:
    
    Hypotheses Tested: {hypotheses}
    Data Results: {execution_results}
    
    CRITICAL CONSTRAINTS:
    1. NO FLUFF: Do not write theoretical "actionable steps" or suggest "algorithms to implement." You must report on the ACTUAL numbers, correlations, and metrics found in the 'Data Results'.
    2. REQUIRED SECTIONS: Format the report strictly with these headers: 
       - 'Executive Summary'
       - 'Key Data Insights' (List the hard numbers and metrics discovered)
       - 'Anomalies & Risks' (Detail the specific anomalies found)
       - 'Strategic Recommendations' (Based ONLY on the actual data results)
    3. Do not mention code, Python, dataframes, or how the data was processed.
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