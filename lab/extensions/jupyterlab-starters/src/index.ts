/**
 * JupyterLab Starters Extension
 *
 * Provides notebook starter templates for common agentic patterns:
 * - HuggingFace Transformers
 * - CrewAI Multi-Agent
 * - LangGraph Workflows
 * - LlamaIndex RAG
 * - MLFlow Experiments
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { LabIcon } from '@jupyterlab/ui-components';

/**
 * Template definitions
 */
interface ITemplate {
  id: string;
  name: string;
  description: string;
  icon: LabIcon;
  category: string;
  cells: Array<{ cell_type: string; source: string[] }>;
}

// Icons for templates
const huggingfaceIconSvg = `
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
</svg>`;

const crewaiIconSvg = `
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
</svg>`;

const langgraphIconSvg = `
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M19.5 3h-15A1.5 1.5 0 003 4.5v15A1.5 1.5 0 004.5 21h15a1.5 1.5 0 001.5-1.5v-15A1.5 1.5 0 0019.5 3zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
</svg>`;

const llamaindexIconSvg = `
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
</svg>`;

const mlflowIconSvg = `
<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
</svg>`;

const huggingfaceIcon = new LabIcon({ name: 'starters:huggingface', svgstr: huggingfaceIconSvg });
const crewaiIcon = new LabIcon({ name: 'starters:crewai', svgstr: crewaiIconSvg });
const langgraphIcon = new LabIcon({ name: 'starters:langgraph', svgstr: langgraphIconSvg });
const llamaindexIcon = new LabIcon({ name: 'starters:llamaindex', svgstr: llamaindexIconSvg });
const mlflowIcon = new LabIcon({ name: 'starters:mlflow', svgstr: mlflowIconSvg });

/**
 * Template definitions
 */
const TEMPLATES: ITemplate[] = [
  {
    id: 'huggingface-starter',
    name: 'HuggingFace Quick Start',
    description: 'Get started with HuggingFace Transformers and smolagents',
    icon: huggingfaceIcon,
    category: 'Agentic',
    cells: [
      {
        cell_type: 'markdown',
        source: [
          '# HuggingFace Quick Start\n',
          '\n',
          'This notebook demonstrates using HuggingFace Transformers and smolagents with the Agentic framework.\n',
          '\n',
          '## Contents\n',
          '1. Environment Setup\n',
          '2. Loading Models from Hub\n',
          '3. Using smolagents\n',
          '4. MLFlow Tracking'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Environment Setup\n',
          'from agentic_assistants import AgenticConfig\n',
          'from agentic_assistants.adapters import HuggingFaceAdapter\n',
          'from agentic_assistants.core import MLFlowTracker\n',
          '\n',
          'config = AgenticConfig()\n',
          'adapter = HuggingFaceAdapter(config)\n',
          'tracker = MLFlowTracker(config)\n',
          '\n',
          'print(f"MLFlow enabled: {tracker.enabled}")\n',
          'print(f"Tracking URI: {config.mlflow.tracking_uri}")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Load a model from HuggingFace Hub\n',
          'from transformers import pipeline\n',
          '\n',
          '# Text generation pipeline\n',
          'generator = pipeline("text-generation", model="gpt2")\n',
          '\n',
          '# Generate text with tracking\n',
          'with tracker.start_run(run_name="hf-generation"):\n',
          '    tracker.log_param("model", "gpt2")\n',
          '    tracker.log_param("task", "text-generation")\n',
          '    \n',
          '    result = generator("Hello, I am a language model,", max_length=50)\n',
          '    \n',
          '    tracker.log_text(result[0]["generated_text"], "output/generated.txt")\n',
          '    print(result[0]["generated_text"])'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Using smolagents for tool-calling agents\n',
          'from smolagents import CodeAgent, HfApiModel, tool\n',
          '\n',
          '@tool\n',
          'def calculator(expression: str) -> float:\n',
          '    """Evaluate a mathematical expression."""\n',
          '    return eval(expression)\n',
          '\n',
          '# Create an agent with tools\n',
          'model = HfApiModel()\n',
          'agent = CodeAgent(tools=[calculator], model=model)\n',
          '\n',
          '# Run the agent\n',
          'result = agent.run("What is 25 * 4 + 10?")\n',
          'print(f"Result: {result}")'
        ]
      }
    ]
  },
  {
    id: 'crewai-starter',
    name: 'CrewAI Multi-Agent',
    description: 'Build multi-agent teams with CrewAI',
    icon: crewaiIcon,
    category: 'Agentic',
    cells: [
      {
        cell_type: 'markdown',
        source: [
          '# CrewAI Multi-Agent Template\n',
          '\n',
          'Build collaborative agent teams with CrewAI and track experiments with MLFlow.\n',
          '\n',
          '## Contents\n',
          '1. Setup and Configuration\n',
          '2. Create Agents with Roles\n',
          '3. Define Tasks\n',
          '4. Run Crew with Tracking'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Setup\n',
          'from agentic_assistants import AgenticConfig\n',
          'from agentic_assistants.adapters import CrewAIAdapter\n',
          '\n',
          'config = AgenticConfig()\n',
          'adapter = CrewAIAdapter(config)\n',
          '\n',
          'print(f"Using model: {adapter.default_model}")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Create agents with specific roles\n',
          'researcher = adapter.create_ollama_agent(\n',
          '    role="Research Analyst",\n',
          '    goal="Find accurate and comprehensive information on topics",\n',
          '    backstory="You are an expert researcher with years of experience "\n',
          '              "in analyzing complex topics and extracting key insights.",\n',
          ')\n',
          '\n',
          'writer = adapter.create_ollama_agent(\n',
          '    role="Content Writer",\n',
          '    goal="Create clear, engaging, and well-structured content",\n',
          '    backstory="You are a skilled writer who can transform research "\n',
          '              "findings into compelling narratives.",\n',
          ')'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Define tasks\n',
          'research_task = adapter.create_task(\n',
          '    description="Research the topic: {topic}. Find key facts, "\n',
          '                "trends, and important information.",\n',
          '    agent=researcher,\n',
          '    expected_output="A comprehensive research summary with key findings.",\n',
          ')\n',
          '\n',
          'writing_task = adapter.create_task(\n',
          '    description="Based on the research, write a clear and engaging "\n',
          '                "article about {topic}.",\n',
          '    agent=writer,\n',
          '    expected_output="A well-structured article ready for publication.",\n',
          ')'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Create and run the crew\n',
          'crew = adapter.create_crew(\n',
          '    agents=[researcher, writer],\n',
          '    tasks=[research_task, writing_task],\n',
          '    verbose=True,\n',
          ')\n',
          '\n',
          '# Run with MLFlow tracking\n',
          'result = adapter.run_crew(\n',
          '    crew,\n',
          '    inputs={"topic": "AI agents in 2024"},\n',
          '    experiment_name="crewai-research",\n',
          '    run_name="research-v1",\n',
          ')\n',
          '\n',
          'print("\\n" + "="*50)\n',
          'print("FINAL OUTPUT:")\n',
          'print("="*50)\n',
          'print(result)'
        ]
      }
    ]
  },
  {
    id: 'langgraph-starter',
    name: 'LangGraph Workflow',
    description: 'Create stateful workflows with LangGraph',
    icon: langgraphIcon,
    category: 'Agentic',
    cells: [
      {
        cell_type: 'markdown',
        source: [
          '# LangGraph Workflow Template\n',
          '\n',
          'Build stateful, multi-step workflows with LangGraph.\n',
          '\n',
          '## Contents\n',
          '1. Setup and State Definition\n',
          '2. Create Nodes\n',
          '3. Build Graph\n',
          '4. Run with Tracking'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Setup\n',
          'from typing import TypedDict, Annotated\n',
          'from agentic_assistants import AgenticConfig\n',
          'from agentic_assistants.adapters import LangGraphAdapter\n',
          '\n',
          'config = AgenticConfig()\n',
          'adapter = LangGraphAdapter(config)'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Define state\n',
          'from langgraph.graph import StateGraph, END\n',
          'from operator import add\n',
          '\n',
          'class WorkflowState(TypedDict):\n',
          '    query: str\n',
          '    steps: Annotated[list[str], add]\n',
          '    result: str'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Create node functions\n',
          'def analyze_query(state: WorkflowState) -> dict:\n',
          '    """Analyze the incoming query."""\n',
          '    return {\n',
          '        "steps": [f"Analyzed: {state[\'query\']}"]\n',
          '    }\n',
          '\n',
          'def process_data(state: WorkflowState) -> dict:\n',
          '    """Process the data based on analysis."""\n',
          '    return {\n',
          '        "steps": ["Processed data"],\n',
          '        "result": f"Result for: {state[\'query\']}"\n',
          '    }\n',
          '\n',
          '# Wrap nodes with tracing\n',
          'analyze_node = adapter.wrap_node(analyze_query, "analyze")\n',
          'process_node = adapter.wrap_node(process_data, "process")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Build the graph\n',
          'graph = adapter.create_state_graph(WorkflowState)\n',
          '\n',
          'graph.add_node("analyze", analyze_node)\n',
          'graph.add_node("process", process_node)\n',
          '\n',
          'graph.set_entry_point("analyze")\n',
          'graph.add_edge("analyze", "process")\n',
          'graph.add_edge("process", END)\n',
          '\n',
          'workflow = graph.compile()'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Run with MLFlow tracking\n',
          'result = adapter.run_graph(\n',
          '    workflow,\n',
          '    inputs={"query": "Analyze market trends", "steps": [], "result": ""},\n',
          '    experiment_name="langgraph-workflow",\n',
          '    run_name="workflow-v1",\n',
          ')\n',
          '\n',
          'print("Steps:", result["steps"])\n',
          'print("Result:", result["result"])'
        ]
      }
    ]
  },
  {
    id: 'llamaindex-starter',
    name: 'LlamaIndex RAG Pipeline',
    description: 'Build RAG pipelines with LlamaIndex',
    icon: llamaindexIcon,
    category: 'Agentic',
    cells: [
      {
        cell_type: 'markdown',
        source: [
          '# LlamaIndex RAG Pipeline\n',
          '\n',
          'Build retrieval-augmented generation pipelines with LlamaIndex.\n',
          '\n',
          '## Contents\n',
          '1. Setup and Configuration\n',
          '2. Load and Index Documents\n',
          '3. Create Query Engine\n',
          '4. Query with Tracking'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Setup\n',
          'from agentic_assistants import AgenticConfig\n',
          'from agentic_assistants.core import MLFlowTracker\n',
          '\n',
          'config = AgenticConfig()\n',
          'tracker = MLFlowTracker(config)\n',
          '\n',
          'print(f"Vector DB backend: {config.vectordb.backend}")\n',
          'print(f"Embedding model: {config.vectordb.embedding_model}")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Configure LlamaIndex with Ollama\n',
          'from llama_index.core import VectorStoreIndex, Document, Settings\n',
          'from llama_index.embeddings.ollama import OllamaEmbedding\n',
          '\n',
          '# Set up embeddings\n',
          'Settings.embed_model = OllamaEmbedding(\n',
          '    model_name=config.vectordb.embedding_model,\n',
          '    base_url=config.ollama.host,\n',
          ')\n',
          '\n',
          'print("Embeddings configured!")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Create sample documents\n',
          'documents = [\n',
          '    Document(text="Agentic AI systems can autonomously plan and execute tasks."),\n',
          '    Document(text="RAG combines retrieval with generation for better accuracy."),\n',
          '    Document(text="MLFlow helps track experiments and model performance."),\n',
          ']\n',
          '\n',
          '# Build index\n',
          'index = VectorStoreIndex.from_documents(documents)\n',
          'print(f"Indexed {len(documents)} documents")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Create query engine and query with tracking\n',
          'query_engine = index.as_query_engine()\n',
          '\n',
          'with tracker.start_run(run_name="rag-query"):\n',
          '    tracker.log_param("index_type", "VectorStoreIndex")\n',
          '    tracker.log_param("num_documents", len(documents))\n',
          '    \n',
          '    query = "What is RAG?"\n',
          '    response = query_engine.query(query)\n',
          '    \n',
          '    tracker.log_param("query", query)\n',
          '    tracker.log_text(str(response), "output/response.txt")\n',
          '    \n',
          '    print(f"Query: {query}")\n',
          '    print(f"Response: {response}")'
        ]
      }
    ]
  },
  {
    id: 'mlflow-starter',
    name: 'MLFlow Experiment',
    description: 'Track and compare experiments with MLFlow',
    icon: mlflowIcon,
    category: 'MLOps',
    cells: [
      {
        cell_type: 'markdown',
        source: [
          '# MLFlow Experiment Tracking\n',
          '\n',
          'Learn to track, compare, and manage experiments with MLFlow.\n',
          '\n',
          '## Contents\n',
          '1. Setup MLFlow Tracking\n',
          '2. Log Parameters and Metrics\n',
          '3. Log Artifacts\n',
          '4. Compare Runs'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Setup\n',
          'from agentic_assistants import AgenticConfig\n',
          'from agentic_assistants.core import MLFlowTracker\n',
          'import time\n',
          '\n',
          'config = AgenticConfig()\n',
          'tracker = MLFlowTracker(config)\n',
          '\n',
          'print(f"MLFlow enabled: {tracker.enabled}")\n',
          'print(f"Tracking URI: {config.mlflow.tracking_uri}")\n',
          'print(f"Experiment: {config.mlflow.experiment_name}")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Run an experiment with tracking\n',
          'with tracker.start_run(run_name="example-run") as run:\n',
          '    # Log parameters\n',
          '    tracker.log_params({\n',
          '        "model": "llama3.2",\n',
          '        "temperature": 0.7,\n',
          '        "max_tokens": 1000,\n',
          '    })\n',
          '    \n',
          '    # Simulate some work and log metrics\n',
          '    for step in range(5):\n',
          '        time.sleep(0.1)  # Simulated processing\n',
          '        tracker.log_metric("step_duration", 0.1, step=step)\n',
          '        tracker.log_metric("accuracy", 0.8 + step * 0.02, step=step)\n',
          '    \n',
          '    # Log final metrics\n',
          '    tracker.log_metrics({\n',
          '        "total_duration": 0.5,\n',
          '        "final_accuracy": 0.88,\n',
          '        "success": 1,\n',
          '    })\n',
          '    \n',
          '    # Log artifacts\n',
          '    tracker.log_text("Experiment completed successfully!\", \"output/summary.txt\")\n',
          '    tracker.log_dict({\"result\": \"success\", \"metrics\": {\"accuracy\": 0.88}}, \"output/results.json\")\n',
          '    \n',
          '    print(f\"Run ID: {run.info.run_id}\")\n',
          '    print(f\"View at: {tracker.get_run_url()}\")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Using the decorator for automatic tracking\n',
          'from agentic_assistants.core import track_experiment\n',
          '\n',
          '@track_experiment("decorated-experiment\", log_args=True)\n',
          'def run_agent_task(topic: str, depth: int = 3):\n',
          '    \"\"\"Run an agent task with automatic tracking.\"\"\"\n',
          '    # Your agent code here\n',
          '    time.sleep(0.2)  # Simulated work\n',
          '    return f\"Analyzed {topic} at depth {depth}\"\n',
          '\n',
          'result = run_agent_task(\"AI trends\", depth=5)\n',
          'print(f\"Result: {result}\")'
        ]
      },
      {
        cell_type: 'code',
        source: [
          '# Query past runs\n',
          'import mlflow\n',
          '\n',
          'mlflow.set_tracking_uri(config.mlflow.tracking_uri)\n',
          '\n',
          '# Search for runs\n',
          'runs = mlflow.search_runs(\n',
          '    experiment_names=[config.mlflow.experiment_name],\n',
          '    max_results=5,\n',
          '    order_by=[\"start_time DESC\"],\n',
          ')\n',
          '\n',
          'if not runs.empty:\n',
          '    print(\"Recent runs:\")\n',
          '    print(runs[[\"run_id\", \"status\", \"start_time\"]].to_string())'
        ]
      }
    ]
  }
];

/**
 * Extension namespace
 */
const NAMESPACE = 'jupyterlab-starters';

/**
 * The starters extension plugin
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@agentic/jupyterlab-starters:plugin',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker, IDocumentManager],
  optional: [ILauncher],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    notebookTracker: INotebookTracker,
    docManager: IDocumentManager,
    launcher: ILauncher | null
  ) => {
    console.log('JupyterLab Starters extension is activated!');

    // Register commands for each template
    TEMPLATES.forEach(template => {
      const commandId = `${NAMESPACE}:${template.id}`;

      app.commands.addCommand(commandId, {
        label: template.name,
        caption: template.description,
        icon: template.icon,
        execute: async () => {
          // Create a new untitled notebook
          const model = await app.commands.execute('notebook:create-new', {
            kernelName: 'python3'
          });

          // Wait for the notebook to be ready
          const widget = notebookTracker.currentWidget;
          if (widget) {
            await widget.revealed;
            await widget.sessionContext.ready;

            // Get the notebook model
            const notebook = widget.content.model;
            if (notebook) {
              // Clear existing cells
              while (notebook.cells.length > 0) {
                notebook.cells.remove(0);
              }

              // Add template cells
              template.cells.forEach(cellData => {
                const cell = notebook.contentFactory.createCell(
                  cellData.cell_type as 'code' | 'markdown',
                  {}
                );
                cell.sharedModel.setSource(cellData.source.join(''));
                notebook.cells.push(cell);
              });
            }
          }
        }
      });

      // Add to command palette
      palette.addItem({
        command: commandId,
        category: 'Notebook Starters'
      });

      // Add to launcher
      if (launcher) {
        launcher.add({
          command: commandId,
          category: template.category,
          rank: TEMPLATES.indexOf(template)
        });
      }
    });
  }
};

export default plugin;

