"""
CrewAI experiment crew for orchestrating scripted fine-tuning experiments.

Defines a multi-agent crew that coordinates dataset preparation, training
configuration, training execution, evaluation, and reporting.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class NemotronExperimentCrew:
    """
    CrewAI-based experiment orchestration crew.

    Agents:
        - DatasetPreparationAgent: curates and prepares training data
        - TrainingOrchestratorAgent: configures and launches training runs
        - EvaluationAgent: runs benchmarks and compares results
        - ReportingAgent: generates experiment reports

    Example:
        >>> crew = NemotronExperimentCrew(project_config=config)
        >>> result = crew.run_experiment(
        ...     name="qlora-code-alpaca-v1",
        ...     dataset_sources=["code-alpaca"],
        ...     training_method="qlora",
        ... )
    """

    def __init__(self, project_config: Optional[Dict[str, Any]] = None):
        self.project_config = project_config or {}
        self._crew = None

    def _build_crew(self):
        """Build the CrewAI crew with all agents and tasks."""
        try:
            from crewai import Agent, Task, Crew, Process

            dataset_agent = Agent(
                role="Dataset Preparation Specialist",
                goal="Curate and prepare high-quality coding datasets for fine-tuning",
                backstory=(
                    "You are an expert in dataset engineering. You evaluate data quality, "
                    "filter noise, deduplicate samples, and produce training-ready datasets."
                ),
                verbose=True,
                allow_delegation=False,
            )

            training_agent = Agent(
                role="Training Orchestrator",
                goal="Configure and launch optimal training runs for nemotron models",
                backstory=(
                    "You are a machine learning engineer specializing in LLM fine-tuning. "
                    "You select hyperparameters, configure LoRA/QLoRA, and monitor training."
                ),
                verbose=True,
                allow_delegation=False,
            )

            eval_agent = Agent(
                role="Evaluation Specialist",
                goal="Evaluate model performance and identify improvements",
                backstory=(
                    "You are an evaluation specialist who runs coding benchmarks, "
                    "analyzes results, and identifies model strengths and weaknesses."
                ),
                verbose=True,
                allow_delegation=False,
            )

            reporting_agent = Agent(
                role="Experiment Reporter",
                goal="Generate clear experiment reports with actionable insights",
                backstory=(
                    "You are a technical writer who turns raw experiment data into "
                    "clear reports with visualizations and recommendations."
                ),
                verbose=True,
                allow_delegation=False,
            )

            prepare_task = Task(
                description=(
                    "Load dataset sources, apply processing pipeline, validate quality, "
                    "and produce training-ready JSONL files."
                ),
                expected_output="Path to processed dataset file and quality statistics",
                agent=dataset_agent,
            )

            configure_task = Task(
                description=(
                    "Select training method, configure hyperparameters, set up LoRA/QLoRA, "
                    "and prepare the training configuration."
                ),
                expected_output="Training configuration with method, hyperparameters, and paths",
                agent=training_agent,
            )

            train_task = Task(
                description="Launch the training job and monitor progress until completion.",
                expected_output="Training job result with metrics and model checkpoint path",
                agent=training_agent,
            )

            evaluate_task = Task(
                description=(
                    "Run HumanEval and MBPP benchmarks on the fine-tuned model "
                    "and compute pass@k, syntax correctness, and code style metrics."
                ),
                expected_output="Evaluation report with per-benchmark metrics",
                agent=eval_agent,
            )

            report_task = Task(
                description=(
                    "Compile experiment results into a report: dataset stats, "
                    "training curves, evaluation metrics, and recommendations."
                ),
                expected_output="Markdown experiment report",
                agent=reporting_agent,
            )

            self._crew = Crew(
                agents=[dataset_agent, training_agent, eval_agent, reporting_agent],
                tasks=[prepare_task, configure_task, train_task, evaluate_task, report_task],
                process=Process.sequential,
                verbose=True,
            )
        except ImportError:
            logger.warning("crewai not installed; crew will run in stub mode")
            self._crew = None

    def run_experiment(
        self,
        name: str,
        dataset_sources: Optional[List[str]] = None,
        training_method: str = "qlora",
        benchmarks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute the full experiment pipeline via CrewAI."""
        logger.info(f"Starting experiment: {name}")

        if self._crew is None:
            self._build_crew()

        if self._crew is not None:
            try:
                inputs = {
                    "experiment_name": name,
                    "dataset_sources": dataset_sources or [],
                    "training_method": training_method,
                    "benchmarks": benchmarks or ["humaneval", "mbpp"],
                    "project_config": self.project_config,
                }
                result = self._crew.kickoff(inputs=inputs)
                return {
                    "experiment": name,
                    "status": "completed",
                    "result": str(result),
                }
            except Exception as e:
                logger.error(f"Crew experiment failed: {e}")
                return {"experiment": name, "status": "failed", "error": str(e)}

        return self._run_stub(name, dataset_sources, training_method, benchmarks)

    def _run_stub(
        self,
        name: str,
        dataset_sources: Optional[List[str]],
        training_method: str,
        benchmarks: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Fallback when CrewAI is not available."""
        logger.info(f"Running stub experiment: {name}")

        from ..training.recipes import SFTRecipe
        recipe = SFTRecipe(project_config=self.project_config)
        result = recipe.run(
            dataset_sources=dataset_sources,
            method=training_method,
        )

        return {
            "experiment": name,
            "status": "completed" if result.success else "failed",
            "stages": result.stages_completed,
            "artifacts": result.artifacts,
            "error": result.error,
        }
