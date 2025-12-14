from langgraph.func import entrypoint,task
from typing_extensions import TypedDict
# Migration Between APIs 
#from functional to graph API 

# ==============================
# BEFORE: FUNCTIONAL API VERSION
# ==============================

# entrypoint marks this function as a Functional API workflow
# checkpointer enables state persistence and recovery between steps
@entrypoint(checkpointer=checkpointer)
def complex_workflow(input_data: dict) -> dict:
    # Execute the first processing step asynchronously
    # .result() blocks until the task finishes and returns its output
    step1 = process_step1(input_data).result()

    # Check whether the output of step1 requires further analysis
    if step1["needs_analysis"]:
        # Run an analysis task if analysis is required
        analysis = analyze_data(step1).result()

        # Check confidence score from analysis output
        if analysis["confidence"] > 0.8:
            # If confidence is high, follow the high-confidence execution path
            result = high_confidence_path(analysis).result()
        else:
            # If confidence is low, follow the low-confidence execution path
            result = low_confidence_path(analysis).result()
    else:
        # If no analysis is needed, take the simple execution path
        result = simple_path(step1).result()

    # Return the final result of the workflow
    return result


# ==================================================
# AFTER: GRAPH API VERSION (STATE-BASED EXECUTION)
# ==================================================

# TypedDict defines the shape of the shared state
# This state is passed between nodes in the graph
class WorkflowState(TypedDict):
    input_data: dict        # Original input to the workflow
    step1_result: dict      # Output from step1 processing
    analysis: dict          # Output from analysis step
    final_result: dict      # Final output of the workflow


# This function determines the next node after "step1"
# It inspects the shared state instead of using inline if-statements
def should_analyze(state):
    # If analysis is required, route to the "analyze" node
    # Otherwise, route to the "simple_path" node
    return "analyze" if state["step1_result"]["needs_analysis"] else "simple_path"


# This function determines the next node after "analyze"
# It replaces the nested confidence-based if/else logic
def confidence_check(state):
    # Route to different nodes based on confidence score
    return "high_confidence" if state["analysis"]["confidence"] > 0.8 else "low_confidence"


# Create a StateGraph using the defined workflow state
workflow = StateGraph(WorkflowState)

# Add a node named "step1" that runs the step1 processing logic
workflow.add_node("step1", process_step1_node)

# Add conditional edges from "step1"
# The should_analyze function decides which node runs next
workflow.add_conditional_edges("step1", should_analyze)

# Add the analysis node
workflow.add_node("analyze", analyze_data_node)

# Add conditional edges from the analysis node
# The confidence_check function decides the next path
workflow.add_conditional_edges("analyze", confidence_check)

# Additional nodes like:
# - simple_path
# - high_confidence
# - low_confidence
# would be added here, along with their edges

