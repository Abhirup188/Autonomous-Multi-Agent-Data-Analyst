from typing import TypedDict,Dict,List,Annotated
import operator

class AgentState(TypedDict):
    file_path:str
    data_profile:str
    hypotheses:Annotated[list,operator.add]
    generated_code:str
    execution_results:str
    anomalies:list
    at_risk_customers:list
    final_report:str
    error_logs:Annotated[list,operator.add]
    automation_status:str
    figures: list
    current_exec_status: str