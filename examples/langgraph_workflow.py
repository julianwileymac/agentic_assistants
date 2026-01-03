"""
LangGraph Workflow Example

This example demonstrates using LangGraph with the Agentic Assistants framework
to create a multi-step workflow with state management.

Usage:
    python examples/langgraph_workflow.py
    # or
    agentic run examples/langgraph_workflow.py --experiment-name "workflow-v1"

Requirements:
    - Ollama installed and running
    - A model pulled (e.g., llama3.2)
    - LangGraph installed (included in project dependencies)
"""

import os
from typing import TypedDict, Annotated, Sequence
from operator import add

from agentic_assistants import AgenticConfig, OllamaManager
from agentic_assistants.adapters import LangGraphAdapter
from agentic_assistants.utils.logging import setup_logging, get_logger

# Set up logging
setup_logging(level="INFO")
logger = get_logger(__name__)


# Define the state for our workflow
class WorkflowState(TypedDict):
    """State that flows through the workflow."""
    query: str
    analysis: str
    response: str
    steps: Annotated[Sequence[str], add]


def create_analysis_workflow(adapter: LangGraphAdapter):
    """
    Create a simple analysis workflow with multiple nodes.
    
    The workflow:
    1. Analyze the query to understand intent
    2. Generate a response based on analysis
    3. Format and finalize the output
    
    Args:
        adapter: LangGraph adapter instance
    
    Returns:
        Compiled workflow graph
    """
    from langgraph.graph import StateGraph, END

    # Create LLM instance
    llm = adapter.create_ollama_llm()

    # Define node functions
    def analyze_query(state: WorkflowState) -> WorkflowState:
        """Analyze the user's query to understand intent."""
        query = state["query"]
        
        prompt = f"""Analyze the following query and identify:
1. The main topic or subject
2. The type of request (question, task, exploration)
3. Key concepts that should be addressed

Query: {query}

Provide a brief structured analysis."""

        response = llm.invoke(prompt)
        
        return {
            "analysis": response.content,
            "steps": ["analysis_complete"],
        }

    def generate_response(state: WorkflowState) -> WorkflowState:
        """Generate a response based on the analysis."""
        query = state["query"]
        analysis = state["analysis"]
        
        prompt = f"""Based on this analysis, provide a helpful response.

Original Query: {query}

Analysis: {analysis}

Provide a clear, informative response that addresses the query."""

        response = llm.invoke(prompt)
        
        return {
            "response": response.content,
            "steps": ["response_generated"],
        }

    def format_output(state: WorkflowState) -> WorkflowState:
        """Format and finalize the output."""
        response = state["response"]
        
        # Could do additional formatting here
        formatted = f"📝 Response:\n\n{response}"
        
        return {
            "response": formatted,
            "steps": ["output_formatted"],
        }

    # Build the graph
    graph = adapter.create_state_graph(WorkflowState)

    # Add nodes with tracing
    graph.add_node("analyze", adapter.wrap_node(analyze_query, "analyze"))
    graph.add_node("generate", adapter.wrap_node(generate_response, "generate"))
    graph.add_node("format", adapter.wrap_node(format_output, "format"))

    # Define edges
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "generate")
    graph.add_edge("generate", "format")
    graph.add_edge("format", END)

    # Compile and return
    return graph.compile()


def main():
    """Run the workflow example."""
    # Get query from environment or use default
    query = os.environ.get(
        "WORKFLOW_QUERY",
        "Explain how multi-agent systems can improve software development workflows"
    )

    logger.info(f"Running workflow with query: {query}")

    # Initialize configuration and Ollama
    config = AgenticConfig()
    ollama = OllamaManager(config)

    # Ensure Ollama is ready
    logger.info("Ensuring Ollama is running...")
    ollama.ensure_running()
    model = ollama.ensure_model()
    logger.info(f"Using model: {model}")

    # Initialize the adapter
    adapter = LangGraphAdapter(config)

    # Create the workflow
    logger.info("Creating workflow graph...")
    workflow = create_analysis_workflow(adapter)

    # Initial state
    initial_state: WorkflowState = {
        "query": query,
        "analysis": "",
        "response": "",
        "steps": [],
    }

    # Run the workflow with tracking
    logger.info("Executing workflow...")
    result = adapter.run_graph(
        workflow,
        inputs=initial_state,
        experiment_name=os.environ.get("MLFLOW_EXPERIMENT_NAME", "langgraph-workflow"),
        run_name="analysis-workflow",
        tags={"example": "workflow"},
    )

    # Print results
    print("\n" + "=" * 60)
    print("WORKFLOW RESULT:")
    print("=" * 60)
    print(f"Steps completed: {result['steps']}")
    print("-" * 60)
    print("Analysis:")
    print(result["analysis"])
    print("-" * 60)
    print("Final Response:")
    print(result["response"])
    print("=" * 60)

    return result


def stream_example():
    """Example showing streaming workflow execution."""
    query = "What are the advantages of using LangGraph for agent workflows?"

    config = AgenticConfig()
    adapter = LangGraphAdapter(config)
    workflow = create_analysis_workflow(adapter)

    initial_state: WorkflowState = {
        "query": query,
        "analysis": "",
        "response": "",
        "steps": [],
    }

    print("Streaming workflow execution:")
    print("-" * 40)

    for state in adapter.stream_graph(
        workflow,
        inputs=initial_state,
        experiment_name="langgraph-streaming",
    ):
        # Print intermediate states as they come
        for key, value in state.items():
            print(f"Node: {key}")
            if isinstance(value, dict):
                if "steps" in value:
                    print(f"  Steps: {value['steps']}")


if __name__ == "__main__":
    try:
        main()
        # Uncomment to see streaming example:
        # stream_example()
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: poetry install")
        raise
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        raise

