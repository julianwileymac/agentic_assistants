"""
Vulnerability Predictor using ML.

Predicts vulnerability exploitability and prioritizes findings.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from pathlib import Path
import pickle
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VulnerabilityPrediction:
    """Vulnerability exploit prediction."""
    vuln_id: str
    exploit_likelihood: float  # 0-1
    priority_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    confidence: float  # 0-1
    factors: Dict[str, float]
    recommendation: str


class VulnerabilityPredictor:
    """
    ML-based vulnerability prioritization and exploit prediction.
    
    Uses features like:
    - CVSS score
    - Age of vulnerability
    - Availability of exploits
    - Asset criticality
    - Attack surface
    
    Example:
        >>> predictor = VulnerabilityPredictor(config)
        >>> prediction = predictor.predict_single(vulnerability)
        >>> priorities = predictor.prioritize(vulnerabilities)
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_path: Optional[str] = None
    ):
        """
        Initialize Vulnerability Predictor.
        
        Args:
            config: Configuration dictionary
            model_path: Path to load pre-trained model
        """
        self.config = config or {}
        self.model_path = model_path
        
        # Model configuration
        self.model_type = self.config.get("model", "random-forest")
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        
        # ML model (lazy loaded)
        self._model = None
        self._scaler = None
        self._is_trained = False
        
        # Feature importance
        self.feature_names = [
            "cvss_score",
            "age_days",
            "has_exploit",
            "asset_criticality",
            "attack_complexity",
            "privileges_required",
            "user_interaction",
            "scope_changed"
        ]
        
        logger.info(f"VulnerabilityPredictor initialized with {self.model_type} model")
    
    @property
    def model(self):
        """Get or create ML model."""
        if self._model is None:
            self._model = self._create_model()
        return self._model
    
    @property
    def scaler(self):
        """Get or create feature scaler."""
        if self._scaler is None:
            self._scaler = self._create_scaler()
        return self._scaler
    
    def _create_model(self):
        """Create ML model."""
        if self.model_type == "random-forest":
            try:
                from sklearn.ensemble import RandomForestClassifier
                model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10,
                    min_samples_split=5
                )
                logger.debug("Created Random Forest model")
                return model
            except ImportError:
                logger.error("scikit-learn not installed")
                return None
        
        elif self.model_type == "gradient-boosting":
            try:
                from sklearn.ensemble import GradientBoostingClassifier
                model = GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=42,
                    max_depth=5
                )
                logger.debug("Created Gradient Boosting model")
                return model
            except ImportError:
                logger.error("scikit-learn not installed")
                return None
        
        else:
            logger.warning(f"Unknown model type: {self.model_type}, using Random Forest")
            try:
                from sklearn.ensemble import RandomForestClassifier
                return RandomForestClassifier(n_estimators=100, random_state=42)
            except ImportError:
                return None
    
    def _create_scaler(self):
        """Create feature scaler."""
        try:
            from sklearn.preprocessing import StandardScaler
            return StandardScaler()
        except ImportError:
            logger.error("scikit-learn not installed")
            return None
    
    def extract_features(self, vulnerability: Any) -> np.ndarray:
        """
        Extract features from vulnerability.
        
        Args:
            vulnerability: Vulnerability object or dict
            
        Returns:
            Feature vector
        """
        # Handle both objects and dicts
        if hasattr(vulnerability, '__dict__'):
            v = vulnerability.__dict__
        else:
            v = vulnerability
        
        features = []
        
        # CVSS score (0-10)
        cvss = v.get("cvss_score", 5.0)
        features.append(cvss if cvss else 5.0)
        
        # Age in days (newer vulnerabilities might be more exploited)
        discovered = v.get("discovered_at", datetime.now().isoformat())
        try:
            discovered_dt = datetime.fromisoformat(discovered)
            age_days = (datetime.now() - discovered_dt).days
        except:
            age_days = 30  # Default to 30 days
        features.append(age_days)
        
        # Has known exploit (1 or 0)
        has_exploit = 1 if v.get("metadata", {}).get("exploit_available") else 0
        features.append(has_exploit)
        
        # Asset criticality (0-10)
        criticality = v.get("metadata", {}).get("asset_criticality", 5.0)
        features.append(criticality)
        
        # Attack complexity (High=1, Low=3)
        complexity_map = {"high": 1, "medium": 2, "low": 3}
        complexity = complexity_map.get(v.get("metadata", {}).get("attack_complexity", "medium"), 2)
        features.append(complexity)
        
        # Privileges required (None=3, Low=2, High=1)
        priv_map = {"none": 3, "low": 2, "high": 1}
        privileges = priv_map.get(v.get("metadata", {}).get("privileges_required", "low"), 2)
        features.append(privileges)
        
        # User interaction (None=2, Required=1)
        interaction = 2 if v.get("metadata", {}).get("user_interaction") == "none" else 1
        features.append(interaction)
        
        # Scope changed (1 or 0)
        scope = 1 if v.get("metadata", {}).get("scope_changed") else 0
        features.append(scope)
        
        return np.array(features).reshape(1, -1)
    
    def train(
        self,
        vulnerabilities: List[Any],
        labels: List[int],
        save_model: bool = True
    ) -> bool:
        """
        Train vulnerability prediction model.
        
        Args:
            vulnerabilities: List of vulnerabilities
            labels: Exploit labels (1 = exploited, 0 = not exploited)
            save_model: Save trained model
            
        Returns:
            True if training succeeded
        """
        if len(vulnerabilities) != len(labels):
            logger.error("Mismatched vulnerabilities and labels")
            return False
        
        logger.info(f"Training on {len(vulnerabilities)} vulnerabilities")
        
        try:
            # Extract features
            X = np.vstack([self.extract_features(v) for v in vulnerabilities])
            y = np.array(labels)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self._is_trained = True
            
            logger.info("Model trained successfully")
            
            # Save if requested
            if save_model and self.model_path:
                self.save(self.model_path)
            
            return True
        
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def predict(
        self,
        vulnerabilities: Union[Any, List[Any]]
    ) -> Union[float, List[float]]:
        """
        Predict exploit likelihood for vulnerabilities.
        
        Args:
            vulnerabilities: Single vulnerability or list
            
        Returns:
            Exploit likelihood (0-1) or list of likelihoods
        """
        single_input = not isinstance(vulnerabilities, list)
        if single_input:
            vulnerabilities = [vulnerabilities]
        
        if not self._is_trained:
            # Return heuristic-based predictions if not trained
            logger.warning("Model not trained, using heuristic predictions")
            predictions = [self._heuristic_prediction(v) for v in vulnerabilities]
            return predictions[0] if single_input else predictions
        
        try:
            # Extract and scale features
            X = np.vstack([self.extract_features(v) for v in vulnerabilities])
            X_scaled = self.scaler.transform(X)
            
            # Predict probabilities
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            
            predictions = probabilities.tolist()
            return predictions[0] if single_input else predictions
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.5 if single_input else [0.5] * len(vulnerabilities)
    
    def _heuristic_prediction(self, vulnerability: Any) -> float:
        """Heuristic-based prediction when model not trained."""
        if hasattr(vulnerability, '__dict__'):
            v = vulnerability.__dict__
        else:
            v = vulnerability
        
        # Simple heuristic based on CVSS and severity
        cvss = v.get("cvss_score", 5.0)
        severity = v.get("severity", "medium")
        
        # Base score from CVSS
        base_score = (cvss or 5.0) / 10.0
        
        # Adjust based on severity
        severity_mult = {
            "critical": 1.2,
            "high": 1.1,
            "medium": 1.0,
            "low": 0.8,
            "info": 0.5
        }
        
        score = base_score * severity_mult.get(severity, 1.0)
        return min(1.0, score)
    
    def predict_single(
        self,
        vulnerability: Any
    ) -> VulnerabilityPrediction:
        """
        Get detailed prediction for a single vulnerability.
        
        Args:
            vulnerability: Vulnerability to analyze
            
        Returns:
            VulnerabilityPrediction with details
        """
        # Get exploit likelihood
        exploit_likelihood = self.predict(vulnerability)
        
        # Extract vulnerability info
        if hasattr(vulnerability, '__dict__'):
            v = vulnerability.__dict__
            vuln_id = getattr(vulnerability, 'vuln_id', 'unknown')
            severity = getattr(vulnerability, 'severity', 'medium')
            cvss = getattr(vulnerability, 'cvss_score', 5.0)
        else:
            v = vulnerability
            vuln_id = v.get('vuln_id', 'unknown')
            severity = v.get('severity', 'medium')
            cvss = v.get('cvss_score', 5.0)
        
        # Calculate priority score
        priority_score = self._calculate_priority(
            exploit_likelihood,
            severity,
            cvss
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(priority_score)
        
        # Calculate confidence
        confidence = self.confidence_threshold if self._is_trained else 0.5
        
        # Get contributing factors
        factors = {
            "exploit_likelihood": exploit_likelihood,
            "cvss_score": (cvss or 5.0) / 10.0,
            "severity_weight": self._severity_weight(severity),
            "has_cve": 1.0 if v.get("cve_id") else 0.0
        }
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            risk_level,
            exploit_likelihood,
            severity
        )
        
        return VulnerabilityPrediction(
            vuln_id=vuln_id,
            exploit_likelihood=exploit_likelihood,
            priority_score=priority_score,
            risk_level=risk_level,
            confidence=confidence,
            factors=factors,
            recommendation=recommendation
        )
    
    def _calculate_priority(
        self,
        exploit_likelihood: float,
        severity: str,
        cvss: Optional[float]
    ) -> float:
        """Calculate priority score (0-100)."""
        # Base score from CVSS
        base = (cvss or 5.0) * 10
        
        # Adjust by exploit likelihood
        base *= (0.5 + 0.5 * exploit_likelihood)
        
        # Adjust by severity
        severity_mult = {
            "critical": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.7,
            "info": 0.3
        }
        base *= severity_mult.get(severity, 1.0)
        
        return min(100, base)
    
    def _severity_weight(self, severity: str) -> float:
        """Get severity weight (0-1)."""
        weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4,
            "info": 0.2
        }
        return weights.get(severity, 0.6)
    
    def _determine_risk_level(self, priority_score: float) -> str:
        """Determine risk level from priority score."""
        if priority_score >= 80:
            return "critical"
        elif priority_score >= 60:
            return "high"
        elif priority_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendation(
        self,
        risk_level: str,
        exploit_likelihood: float,
        severity: str
    ) -> str:
        """Generate remediation recommendation."""
        if risk_level == "critical":
            return "URGENT: Remediate immediately. High exploitation risk."
        elif risk_level == "high":
            return "Prioritize remediation within 24-48 hours."
        elif risk_level == "medium":
            return "Schedule remediation within 1-2 weeks."
        else:
            return "Address during regular maintenance cycle."
    
    def prioritize(
        self,
        vulnerabilities: List[Any]
    ) -> List[tuple]:
        """
        Prioritize vulnerabilities by exploit risk.
        
        Args:
            vulnerabilities: List of vulnerabilities
            
        Returns:
            List of (vulnerability, prediction) tuples, sorted by priority
        """
        logger.info(f"Prioritizing {len(vulnerabilities)} vulnerabilities")
        
        predictions = []
        for vuln in vulnerabilities:
            pred = self.predict_single(vuln)
            predictions.append((vuln, pred))
        
        # Sort by priority score (descending)
        sorted_vulns = sorted(
            predictions,
            key=lambda x: x[1].priority_score,
            reverse=True
        )
        
        return sorted_vulns
    
    def save(self, path: str):
        """Save trained model."""
        try:
            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "config": self.config,
                "feature_names": self.feature_names,
                "is_trained": self._is_trained
            }
            
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load(self, path: str):
        """Load trained model."""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self._model = model_data["model"]
            self._scaler = model_data["scaler"]
            self.config = model_data.get("config", {})
            self.feature_names = model_data.get("feature_names", self.feature_names)
            self._is_trained = model_data.get("is_trained", True)
            
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")


__all__ = ["VulnerabilityPredictor", "VulnerabilityPrediction"]
