"""
Tests for MLFlow tracking integration.
"""

import pytest
from unittest.mock import MagicMock, patch

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, track_experiment


class TestMLFlowTracker:
    """Tests for MLFlowTracker class."""

    def test_init_with_disabled_tracking(self, config):
        """Test initialization with tracking disabled."""
        tracker = MLFlowTracker(config)
        
        assert tracker.enabled is False
        assert tracker.experiment_name == config.mlflow.experiment_name

    def test_init_with_enabled_tracking(self):
        """Test initialization with tracking enabled."""
        config = AgenticConfig(mlflow_enabled=True)
        tracker = MLFlowTracker(config)
        
        assert tracker.enabled is True

    def test_start_run_when_disabled(self, config):
        """Test start_run is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        with tracker.start_run(run_name="test") as run:
            assert run is None

    def test_log_param_when_disabled(self, config):
        """Test log_param is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_param("key", "value")

    def test_log_metric_when_disabled(self, config):
        """Test log_metric is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_metric("accuracy", 0.95)

    def test_log_params_when_disabled(self, config):
        """Test log_params is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_params({"key1": "value1", "key2": "value2"})

    def test_log_metrics_when_disabled(self, config):
        """Test log_metrics is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_metrics({"acc": 0.95, "loss": 0.05})

    def test_set_tag_when_disabled(self, config):
        """Test set_tag is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.set_tag("experiment_type", "test")

    def test_log_artifact_when_disabled(self, config):
        """Test log_artifact is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_artifact("/path/to/file")

    def test_log_text_when_disabled(self, config):
        """Test log_text is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_text("test content", "output.txt")

    def test_log_dict_when_disabled(self, config):
        """Test log_dict is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_dict({"key": "value"}, "config.json")

    def test_get_run_url_when_disabled(self, config):
        """Test get_run_url returns None when disabled."""
        tracker = MLFlowTracker(config)
        
        assert tracker.get_run_url() is None

    def test_log_agent_interaction_when_disabled(self, config):
        """Test log_agent_interaction is a no-op when disabled."""
        tracker = MLFlowTracker(config)
        
        # Should not raise
        tracker.log_agent_interaction(
            agent_name="test_agent",
            input_text="input",
            output_text="output",
            model="llama3.2",
            duration_seconds=1.5,
            tokens_used=100,
        )


class TestTrackExperimentDecorator:
    """Tests for track_experiment decorator."""

    def test_decorator_when_disabled(self, config):
        """Test decorator passes through when tracking disabled."""
        with patch("agentic_assistants.core.mlflow_tracker.AgenticConfig") as mock_config:
            mock_config.return_value = config
            
            @track_experiment("test-exp")
            def my_function(x):
                return x * 2
            
            result = my_function(5)
            assert result == 10

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        @track_experiment("test-exp")
        def my_named_function():
            """My docstring."""
            pass
        
        assert my_named_function.__name__ == "my_named_function"
        assert my_named_function.__doc__ == "My docstring."

