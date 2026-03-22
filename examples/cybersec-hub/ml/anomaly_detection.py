"""
Anomaly Detection for Security Logs.

Uses unsupervised learning to detect anomalous patterns in security logs.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from pathlib import Path
import pickle
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AnomalyResult:
    """Anomaly detection result."""
    scores: List[float]
    anomalies: List[int]  # Indices of anomalous samples
    threshold: float
    model_info: Dict[str, Any]


class AnomalyDetector:
    """
    Anomaly detection for security logs using ML.
    
    Supports multiple algorithms:
    - Isolation Forest (default)
    - One-Class SVM
    - Autoencoder (deep learning)
    
    Example:
        >>> detector = AnomalyDetector(config)
        >>> detector.train(normal_logs)
        >>> anomalies = detector.detect(new_logs)
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_path: Optional[str] = None
    ):
        """
        Initialize Anomaly Detector.
        
        Args:
            config: Configuration dictionary
            model_path: Path to load pre-trained model
        """
        self.config = config or {}
        self.model_path = model_path
        
        # Model configuration
        self.model_type = self.config.get("model", "isolation-forest")
        self.contamination = self.config.get("contamination", 0.05)
        self.min_samples = self.config.get("min_training_samples", 1000)
        
        # ML model (lazy loaded)
        self._model = None
        self._vectorizer = None
        self._is_trained = False
        
        # Training history
        self.training_history = []
        
        logger.info(f"AnomalyDetector initialized with {self.model_type} model")
    
    @property
    def model(self):
        """Get or create ML model."""
        if self._model is None:
            self._model = self._create_model()
        return self._model
    
    @property
    def vectorizer(self):
        """Get or create text vectorizer."""
        if self._vectorizer is None:
            self._vectorizer = self._create_vectorizer()
        return self._vectorizer
    
    def _create_model(self):
        """Create ML model based on configuration."""
        if self.model_type == "isolation-forest":
            try:
                from sklearn.ensemble import IsolationForest
                model = IsolationForest(
                    contamination=self.contamination,
                    random_state=42,
                    n_estimators=100
                )
                logger.debug("Created Isolation Forest model")
                return model
            except ImportError:
                logger.error("scikit-learn not installed. Install with: pip install scikit-learn")
                return None
        
        elif self.model_type == "one-class-svm":
            try:
                from sklearn.svm import OneClassSVM
                model = OneClassSVM(
                    nu=self.contamination,
                    kernel="rbf",
                    gamma="auto"
                )
                logger.debug("Created One-Class SVM model")
                return model
            except ImportError:
                logger.error("scikit-learn not installed")
                return None
        
        elif self.model_type == "autoencoder":
            logger.warning("Autoencoder not yet implemented, falling back to Isolation Forest")
            return self._create_model_isolation_forest()
        
        else:
            logger.error(f"Unknown model type: {self.model_type}")
            return None
    
    def _create_vectorizer(self):
        """Create text vectorizer for log messages."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            logger.debug("Created TF-IDF vectorizer")
            return vectorizer
        except ImportError:
            logger.error("scikit-learn not installed")
            return None
    
    def train(
        self,
        logs: List[str],
        save_model: bool = True
    ) -> bool:
        """
        Train anomaly detection model on normal logs.
        
        Args:
            logs: List of log messages (should be normal/benign)
            save_model: Save trained model to disk
            
        Returns:
            True if training succeeded
        """
        if len(logs) < self.min_samples:
            logger.warning(f"Insufficient training data: {len(logs)} < {self.min_samples}")
            logger.warning("Model may not perform well with limited data")
        
        logger.info(f"Training anomaly detector on {len(logs)} samples")
        
        try:
            # Vectorize logs
            X = self.vectorizer.fit_transform(logs)
            logger.debug(f"Vectorized to shape: {X.shape}")
            
            # Train model
            self.model.fit(X)
            self._is_trained = True
            
            # Record training
            self.training_history.append({
                "timestamp": datetime.now().isoformat(),
                "num_samples": len(logs),
                "model_type": self.model_type,
                "contamination": self.contamination
            })
            
            logger.info("Model trained successfully")
            
            # Save model
            if save_model and self.model_path:
                self.save(self.model_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def detect(
        self,
        logs: Union[str, List[str]],
        return_scores: bool = True
    ) -> Union[List[float], List[int]]:
        """
        Detect anomalies in logs.
        
        Args:
            logs: Log message(s) to analyze
            return_scores: Return anomaly scores (True) or binary labels (False)
            
        Returns:
            Anomaly scores or binary labels (1 = anomaly, -1 = normal)
        """
        if isinstance(logs, str):
            logs = [logs]
        
        if not self._is_trained:
            logger.warning("Model not trained, returning neutral scores")
            return [0.5] * len(logs) if return_scores else [-1] * len(logs)
        
        try:
            # Vectorize
            X = self.vectorizer.transform(logs)
            
            if return_scores:
                # Get anomaly scores (lower is more anomalous)
                scores = self.model.score_samples(X)
                
                # Normalize to 0-1 range (higher = more anomalous)
                normalized_scores = self._normalize_scores(scores)
                
                return normalized_scores.tolist()
            else:
                # Get binary predictions (1 = anomaly, -1 = normal)
                predictions = self.model.predict(X)
                return predictions.tolist()
        
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return [0.5] * len(logs) if return_scores else [-1] * len(logs)
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize anomaly scores to 0-1 range."""
        # Scores are typically negative, more negative = more normal
        # Convert to positive and invert
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score == min_score:
            return np.ones_like(scores) * 0.5
        
        # Normalize and invert (lower raw score = higher anomaly)
        normalized = (scores - min_score) / (max_score - min_score)
        inverted = 1 - normalized
        
        return inverted
    
    def find_anomalies(
        self,
        logs: List[str],
        threshold: float = 0.8
    ) -> AnomalyResult:
        """
        Find anomalous logs above threshold.
        
        Args:
            logs: Log messages to analyze
            threshold: Anomaly score threshold (0-1)
            
        Returns:
            AnomalyResult with details
        """
        scores = self.detect(logs, return_scores=True)
        
        # Find indices of anomalies
        anomaly_indices = [i for i, score in enumerate(scores) if score > threshold]
        
        return AnomalyResult(
            scores=scores,
            anomalies=anomaly_indices,
            threshold=threshold,
            model_info={
                "model_type": self.model_type,
                "is_trained": self._is_trained,
                "total_samples": len(logs),
                "num_anomalies": len(anomaly_indices)
            }
        )
    
    def explain_anomaly(
        self,
        log: str,
        top_features: int = 5
    ) -> Dict[str, Any]:
        """
        Explain why a log is considered anomalous.
        
        Args:
            log: Log message to explain
            top_features: Number of top contributing features
            
        Returns:
            Explanation with key features
        """
        if not self._is_trained:
            return {"error": "Model not trained"}
        
        try:
            # Vectorize
            X = self.vectorizer.transform([log])
            
            # Get feature importance (simplified)
            feature_names = self.vectorizer.get_feature_names_out()
            feature_values = X.toarray()[0]
            
            # Get top features
            top_indices = np.argsort(feature_values)[-top_features:][::-1]
            
            top_features_list = [
                {
                    "feature": feature_names[i],
                    "value": float(feature_values[i])
                }
                for i in top_indices
                if feature_values[i] > 0
            ]
            
            score = self.detect([log], return_scores=True)[0]
            
            return {
                "log": log,
                "anomaly_score": score,
                "is_anomalous": score > 0.8,
                "top_features": top_features_list,
                "explanation": self._generate_explanation(score, top_features_list)
            }
        
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            return {"error": str(e)}
    
    def _generate_explanation(
        self,
        score: float,
        features: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable explanation."""
        if score > 0.9:
            severity = "highly anomalous"
        elif score > 0.8:
            severity = "anomalous"
        elif score > 0.7:
            severity = "potentially anomalous"
        else:
            severity = "normal"
        
        explanation = f"This log is {severity} (score: {score:.2f})."
        
        if features:
            feature_words = [f["feature"] for f in features[:3]]
            explanation += f" Key unusual terms: {', '.join(feature_words)}"
        
        return explanation
    
    def save(self, path: str):
        """Save trained model to disk."""
        try:
            model_data = {
                "model": self.model,
                "vectorizer": self.vectorizer,
                "config": self.config,
                "training_history": self.training_history,
                "is_trained": self._is_trained
            }
            
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load(self, path: str):
        """Load trained model from disk."""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self._model = model_data["model"]
            self._vectorizer = model_data["vectorizer"]
            self.config = model_data.get("config", {})
            self.training_history = model_data.get("training_history", [])
            self._is_trained = model_data.get("is_trained", True)
            
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def retrain(self, logs: List[str]) -> bool:
        """
        Retrain model with new data.
        
        Args:
            logs: New training logs
            
        Returns:
            True if retraining succeeded
        """
        logger.info("Retraining model with new data")
        self._is_trained = False
        return self.train(logs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get model metrics and statistics."""
        return {
            "model_type": self.model_type,
            "is_trained": self._is_trained,
            "training_history": self.training_history,
            "contamination": self.contamination,
            "min_samples": self.min_samples
        }


__all__ = ["AnomalyDetector", "AnomalyResult"]
