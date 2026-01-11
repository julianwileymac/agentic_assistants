"""
Built-in hook implementations.

This module provides ready-to-use hook implementations for common
use cases like MLFlow logging, data validation, and telemetry.

Example:
    >>> from agentic_assistants.hooks import HookManager
    >>> from agentic_assistants.hooks.implementations import MLFlowHook, TelemetryHook
    >>> 
    >>> manager = HookManager()
    >>> manager.register(MLFlowHook())
    >>> manager.register(TelemetryHook())
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import traceback

from agentic_assistants.hooks.specs import hookimpl
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class MLFlowHook:
    """
    Hook for automatic MLFlow experiment tracking.
    
    Logs pipeline runs, node executions, parameters, and metrics
    to MLFlow automatically.
    
    Features:
    - Auto-create experiments per pipeline
    - Log pipeline parameters
    - Track node execution times
    - Record pipeline success/failure
    
    Example:
        >>> from agentic_assistants.hooks import HookManager
        >>> from agentic_assistants.hooks.implementations import MLFlowHook
        >>> 
        >>> manager = HookManager()
        >>> manager.register(MLFlowHook(experiment_name="my_pipeline"))
    """
    
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        tracking_uri: Optional[str] = None,
        log_artifacts: bool = False,
        log_params: bool = True,
        log_metrics: bool = True,
    ):
        """
        Initialize the MLFlow hook.
        
        Args:
            experiment_name: MLFlow experiment name (auto-generated if not provided)
            tracking_uri: MLFlow tracking server URI
            log_artifacts: Whether to log output artifacts
            log_params: Whether to log parameters
            log_metrics: Whether to log execution metrics
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self.log_artifacts = log_artifacts
        self.log_params = log_params
        self.log_metrics = log_metrics
        
        self._mlflow = None
        self._run = None
        self._node_start_times: Dict[str, datetime] = {}
    
    def _get_mlflow(self):
        """Lazy-load MLFlow."""
        if self._mlflow is None:
            try:
                import mlflow
                self._mlflow = mlflow
                
                if self.tracking_uri:
                    mlflow.set_tracking_uri(self.tracking_uri)
            except ImportError:
                logger.warning("MLFlow not installed. Install with: pip install mlflow")
                return None
        return self._mlflow
    
    @hookimpl
    def before_pipeline_run(
        self,
        pipeline: Any,
        catalog: Any,
        run_id: Optional[str] = None,
    ) -> None:
        """Start an MLFlow run for the pipeline."""
        mlflow = self._get_mlflow()
        if not mlflow:
            return
        
        # Set experiment
        experiment_name = self.experiment_name or f"pipeline_{datetime.now().strftime('%Y%m%d')}"
        mlflow.set_experiment(experiment_name)
        
        # Start run
        self._run = mlflow.start_run(run_name=run_id)
        
        # Log pipeline info
        if self.log_params:
            mlflow.log_param("pipeline_nodes", len(pipeline.nodes))
            mlflow.log_param("pipeline_inputs", len(pipeline.inputs))
            mlflow.log_param("pipeline_outputs", len(pipeline.outputs))
        
        logger.info(f"Started MLFlow run: {self._run.info.run_id}")
    
    @hookimpl
    def after_pipeline_run(
        self,
        pipeline: Any,
        run_result: Dict[str, Any],
    ) -> None:
        """End the MLFlow run and log results."""
        mlflow = self._get_mlflow()
        if not mlflow or not self._run:
            return
        
        try:
            if self.log_metrics:
                mlflow.log_metric("success", 1 if run_result.get("success") else 0)
                mlflow.log_metric("error_count", len(run_result.get("errors", [])))
            
            # Log errors as text
            if run_result.get("errors"):
                mlflow.log_text(
                    "\n".join(run_result["errors"]),
                    "errors.txt"
                )
        finally:
            mlflow.end_run()
            self._run = None
            logger.info("Ended MLFlow run")
    
    @hookimpl
    def before_node_run(
        self,
        node: Any,
        inputs: Dict[str, Any],
    ) -> None:
        """Record node start time."""
        self._node_start_times[node.name] = datetime.utcnow()
    
    @hookimpl
    def after_node_run(
        self,
        node: Any,
        outputs: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log node execution metrics."""
        mlflow = self._get_mlflow()
        if not mlflow or not self._run:
            return
        
        start_time = self._node_start_times.pop(node.name, None)
        if start_time and self.log_metrics:
            duration = (datetime.utcnow() - start_time).total_seconds()
            mlflow.log_metric(f"node_{node.name}_duration", duration)
    
    @hookimpl
    def on_node_error(
        self,
        node: Any,
        error: Exception,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log node error to MLFlow."""
        mlflow = self._get_mlflow()
        if not mlflow or not self._run:
            return
        
        mlflow.log_text(
            f"Node: {node.name}\nError: {str(error)}\n\n{traceback.format_exc()}",
            f"errors/node_{node.name}_error.txt"
        )


class DataValidationHook:
    """
    Hook for validating data schemas on load/save.
    
    Validates data against expected schemas using various validation
    backends (pandera, pydantic, cerberus, etc.).
    
    Example:
        >>> hook = DataValidationHook(schemas={
        ...     "users": {
        ...         "columns": ["id", "name", "email"],
        ...         "dtypes": {"id": "int64", "name": "object"},
        ...     }
        ... })
        >>> manager.register(hook)
    """
    
    def __init__(
        self,
        schemas: Optional[Dict[str, Any]] = None,
        strict: bool = False,
        log_warnings: bool = True,
    ):
        """
        Initialize the validation hook.
        
        Args:
            schemas: Dictionary mapping dataset names to schema definitions
            strict: If True, raise exceptions on validation failure
            log_warnings: If True, log warnings for validation issues
        """
        self.schemas = schemas or {}
        self.strict = strict
        self.log_warnings = log_warnings
    
    def add_schema(self, dataset_name: str, schema: Dict[str, Any]) -> None:
        """Add a schema for a dataset."""
        self.schemas[dataset_name] = schema
    
    @hookimpl
    def after_dataset_loaded(
        self,
        dataset_name: str,
        data: Any,
    ) -> Optional[Any]:
        """Validate loaded data against schema."""
        if dataset_name not in self.schemas:
            return None
        
        schema = self.schemas[dataset_name]
        errors = self._validate(data, schema, dataset_name)
        
        if errors:
            error_msg = f"Validation failed for '{dataset_name}':\n" + "\n".join(errors)
            
            if self.strict:
                raise ValueError(error_msg)
            elif self.log_warnings:
                logger.warning(error_msg)
        
        return None  # Don't modify data
    
    @hookimpl
    def before_dataset_saved(
        self,
        dataset_name: str,
        data: Any,
    ) -> Optional[Any]:
        """Validate data before saving."""
        if dataset_name not in self.schemas:
            return None
        
        schema = self.schemas[dataset_name]
        errors = self._validate(data, schema, dataset_name)
        
        if errors:
            error_msg = f"Save validation failed for '{dataset_name}':\n" + "\n".join(errors)
            
            if self.strict:
                raise ValueError(error_msg)
            elif self.log_warnings:
                logger.warning(error_msg)
        
        return None
    
    def _validate(
        self,
        data: Any,
        schema: Dict[str, Any],
        name: str,
    ) -> List[str]:
        """
        Validate data against schema.
        
        Returns list of error messages.
        """
        errors = []
        
        # Check if data is a DataFrame
        try:
            import pandas as pd
            is_dataframe = isinstance(data, pd.DataFrame)
        except ImportError:
            is_dataframe = False
        
        if not is_dataframe:
            return errors
        
        # Validate columns
        if "columns" in schema:
            expected_cols = set(schema["columns"])
            actual_cols = set(data.columns)
            
            missing = expected_cols - actual_cols
            if missing:
                errors.append(f"Missing columns: {missing}")
            
            extra = actual_cols - expected_cols
            if extra and schema.get("strict_columns", False):
                errors.append(f"Extra columns: {extra}")
        
        # Validate dtypes
        if "dtypes" in schema:
            for col, expected_dtype in schema["dtypes"].items():
                if col in data.columns:
                    actual_dtype = str(data[col].dtype)
                    if actual_dtype != expected_dtype:
                        errors.append(
                            f"Column '{col}' has dtype '{actual_dtype}', "
                            f"expected '{expected_dtype}'"
                        )
        
        # Validate not null
        if "not_null" in schema:
            for col in schema["not_null"]:
                if col in data.columns and data[col].isnull().any():
                    null_count = data[col].isnull().sum()
                    errors.append(f"Column '{col}' has {null_count} null values")
        
        # Validate row count range
        if "min_rows" in schema and len(data) < schema["min_rows"]:
            errors.append(
                f"Row count {len(data)} is below minimum {schema['min_rows']}"
            )
        
        if "max_rows" in schema and len(data) > schema["max_rows"]:
            errors.append(
                f"Row count {len(data)} exceeds maximum {schema['max_rows']}"
            )
        
        return errors


class TelemetryHook:
    """
    Hook for recording OpenTelemetry spans and metrics.
    
    Integrates with OTEL to provide distributed tracing for
    pipeline executions.
    
    Example:
        >>> hook = TelemetryHook(service_name="my_pipeline")
        >>> manager.register(hook)
    """
    
    def __init__(
        self,
        service_name: str = "agentic_pipeline",
        enable_tracing: bool = True,
        enable_metrics: bool = True,
    ):
        """
        Initialize the telemetry hook.
        
        Args:
            service_name: Service name for telemetry
            enable_tracing: Enable span tracing
            enable_metrics: Enable metric recording
        """
        self.service_name = service_name
        self.enable_tracing = enable_tracing
        self.enable_metrics = enable_metrics
        
        self._tracer = None
        self._meter = None
        self._spans: Dict[str, Any] = {}
    
    def _init_otel(self):
        """Initialize OpenTelemetry resources."""
        if self._tracer is not None:
            return
        
        try:
            from opentelemetry import trace, metrics
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.metrics import MeterProvider
            
            if self.enable_tracing:
                trace.set_tracer_provider(TracerProvider())
                self._tracer = trace.get_tracer(self.service_name)
            
            if self.enable_metrics:
                metrics.set_meter_provider(MeterProvider())
                self._meter = metrics.get_meter(self.service_name)
        except ImportError:
            logger.debug("OpenTelemetry not installed")
    
    @hookimpl
    def before_pipeline_run(
        self,
        pipeline: Any,
        catalog: Any,
        run_id: Optional[str] = None,
    ) -> None:
        """Start a pipeline span."""
        self._init_otel()
        
        if self._tracer:
            span = self._tracer.start_span(
                "pipeline_run",
                attributes={
                    "pipeline.node_count": len(pipeline.nodes),
                    "run_id": run_id or "unknown",
                },
            )
            self._spans["pipeline"] = span
    
    @hookimpl
    def after_pipeline_run(
        self,
        pipeline: Any,
        run_result: Dict[str, Any],
    ) -> None:
        """End the pipeline span."""
        if "pipeline" in self._spans:
            span = self._spans.pop("pipeline")
            span.set_attribute("success", run_result.get("success", False))
            span.end()
    
    @hookimpl
    def before_node_run(
        self,
        node: Any,
        inputs: Dict[str, Any],
    ) -> None:
        """Start a node span."""
        if self._tracer:
            parent = self._spans.get("pipeline")
            context = trace.set_span_in_context(parent) if parent else None
            
            span = self._tracer.start_span(
                f"node_{node.name}",
                context=context,
                attributes={
                    "node.name": node.name,
                    "node.input_count": len(inputs),
                },
            )
            self._spans[f"node_{node.name}"] = span
    
    @hookimpl
    def after_node_run(
        self,
        node: Any,
        outputs: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """End the node span."""
        span_key = f"node_{node.name}"
        if span_key in self._spans:
            span = self._spans.pop(span_key)
            span.set_attribute("node.output_count", len(outputs))
            span.end()
    
    @hookimpl
    def on_node_error(
        self,
        node: Any,
        error: Exception,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record error on node span."""
        span_key = f"node_{node.name}"
        if span_key in self._spans:
            span = self._spans.pop(span_key)
            span.set_status(trace.StatusCode.ERROR, str(error))
            span.record_exception(error)
            span.end()


class LoggingHook:
    """
    Simple hook for logging pipeline and node execution.
    
    Useful for debugging and monitoring pipeline runs.
    """
    
    def __init__(self, level: str = "INFO"):
        """
        Initialize the logging hook.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.level = level.upper()
        self._log = getattr(logger, self.level.lower(), logger.info)
    
    @hookimpl
    def before_pipeline_run(
        self,
        pipeline: Any,
        catalog: Any,
        run_id: Optional[str] = None,
    ) -> None:
        self._log(f"[Pipeline Start] {len(pipeline)} nodes, run_id={run_id}")
    
    @hookimpl
    def after_pipeline_run(
        self,
        pipeline: Any,
        run_result: Dict[str, Any],
    ) -> None:
        status = "SUCCESS" if run_result.get("success") else "FAILED"
        self._log(f"[Pipeline End] Status: {status}")
    
    @hookimpl
    def before_node_run(
        self,
        node: Any,
        inputs: Dict[str, Any],
    ) -> None:
        self._log(f"[Node Start] {node.name}, inputs: {list(inputs.keys())}")
    
    @hookimpl
    def after_node_run(
        self,
        node: Any,
        outputs: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._log(f"[Node End] {node.name}, outputs: {list(outputs.keys())}")
    
    @hookimpl
    def on_node_error(
        self,
        node: Any,
        error: Exception,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        logger.error(f"[Node Error] {node.name}: {error}")


# Import trace module if available (for TelemetryHook)
try:
    from opentelemetry import trace
except ImportError:
    trace = None
