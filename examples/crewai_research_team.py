"""
CrewAI Research Team Example

This example demonstrates using CrewAI with the Agentic Assistants framework
to create a multi-agent research team that collaborates on a topic.

Usage:
    python examples/crewai_research_team.py
    # or
    agentic run examples/crewai_research_team.py --experiment-name "research-v1"

Requirements:
    - Ollama installed and running
    - A capable model pulled (e.g., llama3.2, mistral)
    - CrewAI installed (included in project dependencies)
"""

import os
from agentic_assistants import AgenticConfig, OllamaManager
from agentic_assistants.adapters import CrewAIAdapter
from agentic_assistants.utils.logging import setup_logging, get_logger

# Set up logging
setup_logging(level="INFO")
logger = get_logger(__name__)


def create_research_crew(adapter: CrewAIAdapter, topic: str):
    """
    Create a research crew with a researcher and writer agent.
    
    Args:
        adapter: CrewAI adapter instance
        topic: Research topic
    
    Returns:
        Configured Crew instance
    """
    # Create the researcher agent
    researcher = adapter.create_ollama_agent(
        role="Senior Research Analyst",
        goal=f"Conduct thorough research on {topic} and identify key insights",
        backstory="""You are an experienced research analyst with expertise in 
        technology and AI. You excel at finding relevant information and 
        synthesizing it into clear insights. You always cite your reasoning 
        and provide structured analysis.""",
        allow_delegation=False,
    )

    # Create the writer agent
    writer = adapter.create_ollama_agent(
        role="Technical Writer",
        goal=f"Create a clear and engaging summary about {topic}",
        backstory="""You are a skilled technical writer who can transform 
        complex research into accessible content. You focus on clarity, 
        accuracy, and engaging presentation. You structure information 
        logically and highlight key takeaways.""",
        allow_delegation=False,
    )

    # Create research task
    research_task = adapter.create_task(
        description=f"""Research the topic: {topic}
        
        Your task:
        1. Identify the main concepts and current state
        2. Find 3-5 key benefits or applications
        3. Note any challenges or limitations
        4. Identify emerging trends
        
        Provide a structured analysis with clear sections.""",
        agent=researcher,
        expected_output="A structured research analysis with sections for concepts, benefits, challenges, and trends.",
    )

    # Create writing task
    writing_task = adapter.create_task(
        description=f"""Based on the research provided, create a concise summary about {topic}.
        
        Your task:
        1. Write an engaging introduction
        2. Summarize the key findings
        3. Highlight practical applications
        4. Conclude with future outlook
        
        Keep it under 500 words and make it accessible to a general audience.""",
        agent=writer,
        expected_output="A well-written summary article under 500 words.",
    )

    # Create the crew
    crew = adapter.create_crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True,
    )

    return crew


def main():
    """Run the research crew example."""
    # Get topic from environment or use default
    topic = os.environ.get("RESEARCH_TOPIC", "Multi-Agent AI Systems")

    logger.info(f"Starting research crew on topic: {topic}")

    # Initialize configuration and Ollama
    config = AgenticConfig()
    ollama = OllamaManager(config)

    # Ensure Ollama is ready
    logger.info("Ensuring Ollama is running...")
    ollama.ensure_running()
    model = ollama.ensure_model()
    logger.info(f"Using model: {model}")

    # Initialize the adapter
    adapter = CrewAIAdapter(config)

    # Create the crew
    logger.info("Creating research crew...")
    crew = create_research_crew(adapter, topic)

    # Run the crew with tracking
    logger.info("Starting crew execution...")
    result = adapter.run_crew(
        crew,
        inputs={"topic": topic},
        experiment_name=os.environ.get("MLFLOW_EXPERIMENT_NAME", "crewai-research"),
        run_name=f"research-{topic.lower().replace(' ', '-')[:20]}",
        tags={"example": "research-team"},
    )

    # Print results
    print("\n" + "=" * 60)
    print("RESEARCH RESULT:")
    print("=" * 60)
    print(result)
    print("=" * 60)

    return result


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: poetry install")
        raise
    except Exception as e:
        logger.error(f"Error running crew: {e}")
        raise

