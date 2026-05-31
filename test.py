import pandas as pd
import os
from main import profiler_node, strategist_node, CoderNode, executor_node, Reporter_node,automator_node

data = {
    'OrderID': [1, 2, 3, 4, 5],
    'Customer': ['Alice', 'Bob', 'Charlie', 'Alice', 'Eve'],
    'Sales': [250.0, 150.0, 300.0, 50.0, 500.0],
    'Date': ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04', '2026-01-05']
}
df_test = pd.DataFrame(data)
test_csv_path = "test_sales.csv"
df_test.to_csv(test_csv_path, index=False)

mock_state = {
    "file_path": test_csv_path,
    "data_profile": "",
    "hypotheses": [],
    "generated_code": "",
    "execution_results": "",
    "anomalies": [],
    "at_risk_customers": [],
    "final_report": "",
    "error_logs": []
}

try:
    print("--- Starting Node Test ---")
    
    result1 = profiler_node(mock_state)
    print("SUCCESS: Profiler_Node returned a result.")
    mock_state.update(result1)
    
    result2 = strategist_node(mock_state)
    print("SUCCESS: Strategist_Node returned a result.")
    mock_state.update(result2)
    
    result3 = CoderNode(mock_state)
    mock_state.update(result3)
    if "Error" in mock_state.get("generated_code", ""):
        print("\nHALTING PIPELINE: Coder Node failed (Likely API Rate Limit).")
    else:
        print("SUCCESS: Coder Node Generated The Code")
        
        result4 = executor_node(mock_state)
        print("SUCCESS: Execution Node Finished")
        mock_state.update(result4)
        
        if "error_logs" in result4 and result4["error_logs"]:
            print("\nHALTING PIPELINE: Execution failed. Skipping Reporter Node.")
            print("Execution Error:", result4["error_logs"])
        else:
            result5 = Reporter_node(mock_state)
            print("SUCCESS: Report Generated Successfully")
            print(result5)
            mock_state.update(result5)
            
            result6 = automator_node(mock_state)
            print("Automation Done")
except Exception as e:
    print(f"FAILURE: Pipeline crashed with global error: {e}")

finally:
    if os.path.exists(test_csv_path):
        os.remove(test_csv_path)