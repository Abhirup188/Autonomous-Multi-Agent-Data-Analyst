
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from main import profiler_node,strategist_node,CoderNode,executor_node,Reporter_node,automator_node

memory = MemorySaver()

def should_continue_coder_executor(state:AgentState):
    if "Error" in state.get("generated_code",""):
        return "end"
    else:
        return "continue"
    
def executor_router(state: AgentState):
    status = state.get("current_exec_status")
    if status == "success":
        print("Execution Successful! Moving to Reporter.")
        return "success"

    errors = state.get("error_logs", [])
    if len(errors) >= 3:
        print("MAX RETRIES REACHED. ABORTING.")
        return "end"
        
    print(f"Execution Failed. Routing back to Coder for self-healing (Attempt {len(errors)}/3)...")
    return "retry"


workflow = StateGraph(AgentState)
workflow.add_node("profiler",profiler_node)
workflow.add_node("strategist",strategist_node)
workflow.add_node("Coder",CoderNode)
workflow.add_node("executor",executor_node)
workflow.add_node("Reporter",Reporter_node)
workflow.add_node("Automator",automator_node)

workflow.set_entry_point("profiler")

workflow.add_edge("profiler","strategist")
workflow.add_edge("strategist","Coder")

workflow.add_conditional_edges(
    "Coder",
    should_continue_coder_executor,
    {
        "continue":"executor",
        "end":END
    }
)

workflow.add_conditional_edges(
    "executor",
    executor_router,
    {
        "retry": "Coder",
        "success": "Reporter",
        "end": END
    }
)

workflow.add_edge("Reporter","Automator")
workflow.add_edge("Automator",END)
app = workflow.compile(checkpointer=memory)

