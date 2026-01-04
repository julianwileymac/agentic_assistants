"""
HuggingFace framework adapter with integrated observability.

This adapter wraps HuggingFace Transformers and Hub functionality to provide:
- MLFlow experiment tracking for model inference
- OpenTelemetry tracing for pipeline executions
- Model downloading and caching from Hub
- Standardized metrics and logging

Example:
    >>> from agentic_assistants.adapters import HuggingFaceAdapter
    >>> 
    >>> adapter = HuggingFaceAdapter()
    >>> 
    >>> # Use a text generation pipeline
    >>> generator = adapter.create_pipeline("text-generation", model="gpt2")
    >>> result = adapter.run_pipeline(
    ...     generator,
    ...     "Hello, I am a language model,",
    ...     experiment_name="hf-generation"
    ... )
    >>> 
    >>> # Download a model from Hub
    >>> model_path = adapter.download_model("meta-llama/Llama-2-7b-chat-hf")
"""

import time
from pathlib import Path
from typing import Any, Callable, Optional, Union

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class HuggingFaceAdapter(BaseAdapter):
    """
    Adapter for HuggingFace Transformers and Hub integration.
    
    This adapter provides observability wrappers for HuggingFace pipelines
    and model operations, tracking inference, model loading, and Hub downloads.
    
    Attributes:
        config: Agentic configuration instance
        cache_dir: Directory for caching downloaded models
        default_device: Default device for model inference
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        cache_dir: Optional[Path] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the HuggingFace adapter.
        
        Args:
            config: Configuration instance
            cache_dir: Directory for model cache (uses HF default if None)
            device: Device for inference ('cpu', 'cuda', 'mps', or 'auto')
        """
        super().__init__(config, name="HuggingFace")
        self.cache_dir = cache_dir or Path.home() / ".cache" / "huggingface"
        self.default_device = device or "auto"
        self._pipelines: dict[str, Any] = {}

    def run(self, pipeline: Any, inputs: Any, **kwargs) -> Any:
        """
        Run a HuggingFace pipeline with tracking.
        
        This is a convenience method that calls run_pipeline.
        
        Args:
            pipeline: The HuggingFace pipeline
            inputs: Input for the pipeline
            **kwargs: Additional arguments passed to run_pipeline
        
        Returns:
            Pipeline output
        """
        return self.run_pipeline(pipeline, inputs, **kwargs)

    def create_pipeline(
        self,
        task: str,
        model: Optional[str] = None,
        device: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a HuggingFace pipeline with tracking.
        
        Args:
            task: Pipeline task (e.g., 'text-generation', 'sentiment-analysis')
            model: Model name or path
            device: Device for inference
            **kwargs: Additional pipeline arguments
        
        Returns:
            Configured HuggingFace pipeline
        
        Example:
            >>> generator = adapter.create_pipeline(
            ...     "text-generation",
            ...     model="gpt2",
            ...     device="cuda"
            ... )
        """
        try:
            from transformers import pipeline
        except ImportError as e:
            raise ImportError(
                "transformers is required. Install with: pip install transformers"
            ) from e

        with self.telemetry.span(
            "huggingface.create_pipeline",
            attributes={
                "task": task,
                "model": model or "default",
                "device": device or self.default_device,
            },
        ) as span_logger:
            start_time = time.time()
            
            try:
                pipe = pipeline(
                    task,
                    model=model,
                    device=device or self.default_device,
                    **kwargs,
                )
                
                duration = time.time() - start_time
                span_logger.log_event("pipeline_created", {
                    "task": task,
                    "model": model,
                    "duration_seconds": duration,
                })
                
                # Cache the pipeline
                cache_key = f"{task}:{model or 'default'}"
                self._pipelines[cache_key] = pipe
                
                logger.info(f"Created {task} pipeline with model {model} in {duration:.2f}s")
                return pipe
                
            except Exception as e:
                span_logger.log_error(e)
                raise

    def run_pipeline(
        self,
        pipeline: Any,
        inputs: Any,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> Any:
        """
        Run a HuggingFace pipeline with full observability.
        
        Args:
            pipeline: The HuggingFace pipeline to run
            inputs: Input for the pipeline
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
            **kwargs: Additional pipeline arguments
        
        Returns:
            Pipeline output
        
        Example:
            >>> result = adapter.run_pipeline(
            ...     generator,
            ...     "Once upon a time",
            ...     experiment_name="story-generation",
            ...     max_length=100
            ... )
        """
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Determine task and model from pipeline
        task = getattr(pipeline, 'task', 'unknown')
        model_name = getattr(pipeline.model.config, '_name_or_path', 'unknown')
        
        # Build run name
        actual_run_name = run_name or f"pipeline-{task}-{time.strftime('%Y%m%d-%H%M%S')}"

        # Build parameters
        params = {
            "framework": "huggingface",
            "task": task,
            "model": model_name,
            **{k: str(v) for k, v in kwargs.items()},
        }

        # Build tags
        all_tags = {"framework": "huggingface", "task": task}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params) as (mlflow_run, span_logger):
            start_time = time.time()

            try:
                logger.info(f"Running {task} pipeline: {actual_run_name}")
                span_logger.log_input(inputs)

                # Run the pipeline
                result = pipeline(inputs, **kwargs)

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Log output
                span_logger.log_output(result)
                
                # Try to log token counts if available
                self._log_token_metrics(inputs, result, span_logger)

                # Log result summary
                if isinstance(result, list) and len(result) > 0:
                    self.tracker.log_dict(
                        {"results": [str(r)[:500] for r in result[:5]]},
                        "output/results.json",
                    )

                logger.info(f"Pipeline completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                span_logger.log_error(e)
                logger.error(f"Pipeline failed after {duration:.2f}s: {e}")
                raise

    def _log_token_metrics(
        self,
        inputs: Any,
        outputs: Any,
        span_logger: Any,
    ) -> None:
        """Log token-related metrics if available."""
        try:
            # Estimate input tokens (rough approximation)
            input_text = str(inputs) if not isinstance(inputs, str) else inputs
            input_tokens = len(input_text.split())
            
            # Estimate output tokens
            if isinstance(outputs, list) and len(outputs) > 0:
                output_text = str(outputs[0].get('generated_text', outputs[0]))
                output_tokens = len(output_text.split())
            else:
                output_tokens = 0
            
            span_logger.log_llm_call(
                model="huggingface",
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
            )
            
            self.tracker.log_metrics({
                "tokens_input_estimate": input_tokens,
                "tokens_output_estimate": output_tokens,
            })
        except Exception:
            pass  # Token logging is best-effort

    def download_model(
        self,
        model_id: str,
        revision: Optional[str] = None,
        token: Optional[str] = None,
        force_download: bool = False,
    ) -> Path:
        """
        Download a model from HuggingFace Hub.
        
        Args:
            model_id: Model identifier on HuggingFace Hub
            revision: Specific revision (branch, tag, or commit)
            token: HuggingFace API token for private models
            force_download: Force re-download even if cached
        
        Returns:
            Path to the downloaded model
        
        Example:
            >>> model_path = adapter.download_model(
            ...     "meta-llama/Llama-2-7b-chat-hf",
            ...     token="hf_..."
            ... )
        """
        try:
            from huggingface_hub import snapshot_download
        except ImportError as e:
            raise ImportError(
                "huggingface_hub is required. Install with: pip install huggingface_hub"
            ) from e

        with self.telemetry.span(
            "huggingface.download_model",
            attributes={
                "model_id": model_id,
                "revision": revision or "main",
                "force_download": force_download,
            },
        ) as span_logger:
            start_time = time.time()
            
            try:
                logger.info(f"Downloading model: {model_id}")
                span_logger.log_event("download_started", {"model_id": model_id})
                
                model_path = snapshot_download(
                    repo_id=model_id,
                    revision=revision,
                    token=token,
                    cache_dir=str(self.cache_dir),
                    force_download=force_download,
                )
                
                duration = time.time() - start_time
                
                span_logger.log_event("download_completed", {
                    "model_id": model_id,
                    "path": str(model_path),
                    "duration_seconds": duration,
                })
                
                self.tracker.log_params({
                    "downloaded_model": model_id,
                    "model_path": str(model_path),
                })
                self.tracker.log_metric("download_duration_seconds", duration)
                
                logger.info(f"Downloaded {model_id} to {model_path} in {duration:.2f}s")
                return Path(model_path)
                
            except Exception as e:
                span_logger.log_error(e)
                logger.error(f"Failed to download {model_id}: {e}")
                raise

    def list_hub_models(
        self,
        filter_task: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        List models from HuggingFace Hub.
        
        Args:
            filter_task: Filter by pipeline task
            search: Search query
            limit: Maximum number of results
        
        Returns:
            List of model information dictionaries
        """
        try:
            from huggingface_hub import HfApi
        except ImportError as e:
            raise ImportError(
                "huggingface_hub is required. Install with: pip install huggingface_hub"
            ) from e

        api = HfApi()
        
        models = api.list_models(
            filter=filter_task,
            search=search,
            limit=limit,
            sort="downloads",
            direction=-1,
        )
        
        return [
            {
                "id": m.id,
                "downloads": m.downloads,
                "likes": m.likes,
                "tags": m.tags,
            }
            for m in models
        ]

    def load_model(
        self,
        model_id: str,
        model_class: Optional[str] = None,
        device: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Load a model from HuggingFace.
        
        Args:
            model_id: Model identifier or path
            model_class: Model class name (e.g., 'AutoModelForCausalLM')
            device: Device for the model
            **kwargs: Additional model arguments
        
        Returns:
            Loaded model
        
        Example:
            >>> model = adapter.load_model(
            ...     "gpt2",
            ...     model_class="AutoModelForCausalLM",
            ...     device="cuda"
            ... )
        """
        try:
            from transformers import AutoModel, AutoModelForCausalLM, AutoModelForSeq2SeqLM
        except ImportError as e:
            raise ImportError(
                "transformers is required. Install with: pip install transformers"
            ) from e

        # Map class names to classes
        model_classes = {
            "AutoModel": AutoModel,
            "AutoModelForCausalLM": AutoModelForCausalLM,
            "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,
        }

        with self.telemetry.span(
            "huggingface.load_model",
            attributes={
                "model_id": model_id,
                "model_class": model_class or "AutoModel",
                "device": device or self.default_device,
            },
        ) as span_logger:
            start_time = time.time()
            
            try:
                cls = model_classes.get(model_class, AutoModel)
                model = cls.from_pretrained(model_id, **kwargs)
                
                if device:
                    model = model.to(device)
                
                duration = time.time() - start_time
                
                span_logger.log_event("model_loaded", {
                    "model_id": model_id,
                    "duration_seconds": duration,
                })
                
                logger.info(f"Loaded model {model_id} in {duration:.2f}s")
                return model
                
            except Exception as e:
                span_logger.log_error(e)
                raise

    def load_tokenizer(self, model_id: str, **kwargs) -> Any:
        """
        Load a tokenizer from HuggingFace.
        
        Args:
            model_id: Model/tokenizer identifier
            **kwargs: Additional tokenizer arguments
        
        Returns:
            Loaded tokenizer
        """
        try:
            from transformers import AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "transformers is required. Install with: pip install transformers"
            ) from e

        with self.telemetry.span(
            "huggingface.load_tokenizer",
            attributes={"model_id": model_id},
        ) as span_logger:
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_id, **kwargs)
                span_logger.log_event("tokenizer_loaded", {"model_id": model_id})
                return tokenizer
            except Exception as e:
                span_logger.log_error(e)
                raise

    def generate(
        self,
        model: Any,
        tokenizer: Any,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        experiment_name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text using a model and tokenizer with full tracking.
        
        Args:
            model: The loaded model
            tokenizer: The loaded tokenizer
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            experiment_name: MLFlow experiment name
            **kwargs: Additional generation arguments
        
        Returns:
            Generated text
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        run_name = f"generate-{time.strftime('%Y%m%d-%H%M%S')}"
        
        params = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            **{k: str(v) for k, v in kwargs.items()},
        }

        with self.track_run(run_name, params=params) as (mlflow_run, span_logger):
            with self.track_llm_call(
                model=str(getattr(model.config, '_name_or_path', 'unknown')),
                operation="generate",
                temperature=temperature,
            ) as llm_span:
                start_time = time.time()
                
                try:
                    # Tokenize input
                    inputs = tokenizer(prompt, return_tensors="pt")
                    if hasattr(model, 'device'):
                        inputs = {k: v.to(model.device) for k, v in inputs.items()}
                    
                    input_tokens = inputs['input_ids'].shape[-1]
                    
                    # Generate
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        do_sample=temperature > 0,
                        **kwargs,
                    )
                    
                    # Decode
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    output_tokens = outputs.shape[-1] - input_tokens
                    
                    duration = time.time() - start_time
                    
                    # Log metrics
                    llm_span.log_llm_call(
                        model=str(getattr(model.config, '_name_or_path', 'unknown')),
                        prompt_tokens=input_tokens,
                        completion_tokens=output_tokens,
                        temperature=temperature,
                    )
                    
                    self.tracker.log_metrics({
                        "tokens_input": input_tokens,
                        "tokens_output": output_tokens,
                        "duration_seconds": duration,
                        "tokens_per_second": output_tokens / duration if duration > 0 else 0,
                    })
                    
                    self.tracker.log_text(generated_text, "output/generated.txt")
                    
                    return generated_text
                    
                except Exception as e:
                    span_logger.log_error(e)
                    raise

