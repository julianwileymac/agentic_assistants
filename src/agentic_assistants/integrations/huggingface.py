"""
HuggingFace Hub integration.

This module provides integration with HuggingFace Hub for:
- Model storage and versioning
- Dataset hosting
- Model cards generation
- Inference API integration

Example:
    >>> from agentic_assistants.integrations.huggingface import HuggingFaceHubIntegration
    >>> 
    >>> hf = HuggingFaceHubIntegration(token="hf_xxx")
    >>> 
    >>> # Push a model
    >>> hf.push_model(
    ...     model_path="./outputs/my-model",
    ...     repo_id="username/my-model",
    ...     model_card=model_card,
    ... )
    >>> 
    >>> # Pull a model
    >>> local_path = hf.pull_model("username/my-model")
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ModelCard:
    """HuggingFace model card content."""
    
    # Basic info
    model_name: str
    base_model: str
    description: str
    
    # Training info
    training_method: str = ""
    training_framework: str = ""
    training_dataset: str = ""
    
    # Performance
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Usage
    usage_example: str = ""
    intended_uses: str = ""
    limitations: str = ""
    
    # Technical
    language: str = "en"
    license: str = "apache-2.0"
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_markdown(self) -> str:
        """Generate model card markdown."""
        card = f"""---
license: {self.license}
language:
- {self.language}
tags:
{chr(10).join(f'- {tag}' for tag in self.tags)}
base_model: {self.base_model}
---

# {self.model_name}

{self.description}

## Model Details

- **Base Model**: {self.base_model}
- **Training Method**: {self.training_method}
- **Training Framework**: {self.training_framework}
- **Training Dataset**: {self.training_dataset}

## Performance

"""
        if self.metrics:
            card += "| Metric | Value |\n|--------|-------|\n"
            for metric, value in self.metrics.items():
                card += f"| {metric} | {value:.4f} |\n"
        
        card += f"""
## Usage

```python
{self.usage_example or 'from transformers import AutoModelForCausalLM, AutoTokenizer'}

{self.usage_example or f'model = AutoModelForCausalLM.from_pretrained("{self.model_name}")'}
{'' if self.usage_example else f'tokenizer = AutoTokenizer.from_pretrained("{self.model_name}")'}
```

## Intended Uses

{self.intended_uses or 'This model is intended for research and development purposes.'}

## Limitations

{self.limitations or 'This model may produce biased or inaccurate outputs. Use with caution.'}

## Training Details

- Created: {self.created_at}
"""
        return card


@dataclass
class DatasetCard:
    """HuggingFace dataset card content."""
    
    name: str
    description: str
    
    # Dataset info
    format: str = "json"
    num_samples: int = 0
    features: Dict[str, str] = field(default_factory=dict)
    
    # Usage
    task_categories: List[str] = field(default_factory=list)
    language: str = "en"
    license: str = "apache-2.0"
    tags: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Generate dataset card markdown."""
        card = f"""---
license: {self.license}
task_categories:
{chr(10).join(f'- {cat}' for cat in self.task_categories)}
language:
- {self.language}
tags:
{chr(10).join(f'- {tag}' for tag in self.tags)}
---

# {self.name}

{self.description}

## Dataset Details

- **Format**: {self.format}
- **Number of Samples**: {self.num_samples:,}

## Features

"""
        if self.features:
            card += "| Feature | Type |\n|---------|------|\n"
            for feature, dtype in self.features.items():
                card += f"| {feature} | {dtype} |\n"
        
        return card


class HuggingFaceHubIntegration:
    """
    HuggingFace Hub integration for models and datasets.
    
    Provides:
    - Push/pull models to HuggingFace Hub
    - Push/pull datasets
    - Model card generation and management
    - Automatic fallback to local storage
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        default_to_local: bool = True,
        local_cache_dir: Optional[str] = None,
    ):
        """
        Initialize HuggingFace Hub integration.
        
        Args:
            token: HuggingFace API token (or set HF_TOKEN env var)
            default_to_local: Fall back to local storage if Hub unavailable
            local_cache_dir: Local cache directory for models
        """
        self.token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        self.default_to_local = default_to_local
        self.local_cache_dir = Path(local_cache_dir or "./data/models/cache")
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._hub_available = self._check_hub()
    
    def _check_hub(self) -> bool:
        """Check if HuggingFace Hub is available."""
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            # Simple check
            return True
        except ImportError:
            logger.warning("huggingface_hub not installed. Install with: pip install huggingface-hub")
            return False
        except Exception as e:
            logger.warning(f"HuggingFace Hub not available: {e}")
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if Hub integration is available."""
        return self._hub_available and self.token is not None
    
    # =========================================================================
    # Model Operations
    # =========================================================================
    
    def push_model(
        self,
        model_path: str,
        repo_id: str,
        model_card: Optional[ModelCard] = None,
        private: bool = False,
        commit_message: str = "Upload model",
    ) -> Dict[str, Any]:
        """
        Push a model to HuggingFace Hub.
        
        Args:
            model_path: Local path to model
            repo_id: HuggingFace repo ID (username/model-name)
            model_card: Optional model card
            private: Make repo private
            commit_message: Commit message
        
        Returns:
            Result dictionary with success status and URL
        """
        if not self.is_available:
            if self.default_to_local:
                return self._save_model_locally(model_path, repo_id, model_card)
            return {"success": False, "error": "HuggingFace Hub not available"}
        
        try:
            from huggingface_hub import HfApi, create_repo
            
            api = HfApi(token=self.token)
            
            # Create repo if it doesn't exist
            try:
                create_repo(repo_id, token=self.token, private=private, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create repo: {e}")
            
            # Upload model files
            api.upload_folder(
                folder_path=model_path,
                repo_id=repo_id,
                commit_message=commit_message,
            )
            
            # Upload model card if provided
            if model_card:
                readme_content = model_card.to_markdown()
                api.upload_file(
                    path_or_fileobj=readme_content.encode(),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    commit_message="Update model card",
                )
            
            url = f"https://huggingface.co/{repo_id}"
            logger.info(f"Pushed model to {url}")
            
            return {
                "success": True,
                "repo_id": repo_id,
                "url": url,
            }
            
        except Exception as e:
            logger.error(f"Failed to push model: {e}")
            if self.default_to_local:
                return self._save_model_locally(model_path, repo_id, model_card)
            return {"success": False, "error": str(e)}
    
    def pull_model(
        self,
        repo_id: str,
        revision: Optional[str] = None,
        local_dir: Optional[str] = None,
    ) -> Optional[str]:
        """
        Pull a model from HuggingFace Hub.
        
        Args:
            repo_id: HuggingFace repo ID
            revision: Specific revision/branch
            local_dir: Local directory to save to
        
        Returns:
            Local path to downloaded model
        """
        if not self._hub_available:
            # Check local cache
            local_path = self.local_cache_dir / repo_id.replace("/", "_")
            if local_path.exists():
                return str(local_path)
            return None
        
        try:
            from huggingface_hub import snapshot_download
            
            local_dir = local_dir or str(self.local_cache_dir / repo_id.replace("/", "_"))
            
            path = snapshot_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=local_dir,
                token=self.token,
            )
            
            logger.info(f"Downloaded model to {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return None
    
    def _save_model_locally(
        self,
        model_path: str,
        repo_id: str,
        model_card: Optional[ModelCard] = None,
    ) -> Dict[str, Any]:
        """Save model to local storage as fallback."""
        import shutil
        
        local_path = self.local_cache_dir / repo_id.replace("/", "_")
        local_path.mkdir(parents=True, exist_ok=True)
        
        # Copy model files
        src = Path(model_path)
        if src.is_dir():
            for item in src.iterdir():
                if item.is_file():
                    shutil.copy2(item, local_path / item.name)
                elif item.is_dir():
                    shutil.copytree(item, local_path / item.name, dirs_exist_ok=True)
        
        # Save model card
        if model_card:
            with open(local_path / "README.md", "w") as f:
                f.write(model_card.to_markdown())
        
        logger.info(f"Saved model locally to {local_path}")
        
        return {
            "success": True,
            "local_path": str(local_path),
            "storage": "local",
        }
    
    # =========================================================================
    # Dataset Operations
    # =========================================================================
    
    def push_dataset(
        self,
        dataset_path: str,
        repo_id: str,
        dataset_card: Optional[DatasetCard] = None,
        private: bool = False,
    ) -> Dict[str, Any]:
        """
        Push a dataset to HuggingFace Hub.
        
        Args:
            dataset_path: Local path to dataset
            repo_id: HuggingFace repo ID
            dataset_card: Optional dataset card
            private: Make repo private
        
        Returns:
            Result dictionary
        """
        if not self.is_available:
            if self.default_to_local:
                return self._save_dataset_locally(dataset_path, repo_id, dataset_card)
            return {"success": False, "error": "HuggingFace Hub not available"}
        
        try:
            from huggingface_hub import HfApi, create_repo
            
            api = HfApi(token=self.token)
            
            # Create dataset repo
            create_repo(
                repo_id,
                token=self.token,
                private=private,
                repo_type="dataset",
                exist_ok=True,
            )
            
            # Upload dataset files
            api.upload_folder(
                folder_path=dataset_path,
                repo_id=repo_id,
                repo_type="dataset",
            )
            
            # Upload dataset card
            if dataset_card:
                readme_content = dataset_card.to_markdown()
                api.upload_file(
                    path_or_fileobj=readme_content.encode(),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="dataset",
                )
            
            url = f"https://huggingface.co/datasets/{repo_id}"
            logger.info(f"Pushed dataset to {url}")
            
            return {
                "success": True,
                "repo_id": repo_id,
                "url": url,
            }
            
        except Exception as e:
            logger.error(f"Failed to push dataset: {e}")
            if self.default_to_local:
                return self._save_dataset_locally(dataset_path, repo_id, dataset_card)
            return {"success": False, "error": str(e)}
    
    def pull_dataset(
        self,
        repo_id: str,
        local_dir: Optional[str] = None,
    ) -> Optional[str]:
        """
        Pull a dataset from HuggingFace Hub.
        
        Args:
            repo_id: HuggingFace dataset repo ID
            local_dir: Local directory to save to
        
        Returns:
            Local path to downloaded dataset
        """
        if not self._hub_available:
            return None
        
        try:
            from huggingface_hub import snapshot_download
            
            local_dir = local_dir or str(self.local_cache_dir / "datasets" / repo_id.replace("/", "_"))
            
            path = snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=local_dir,
                token=self.token,
            )
            
            logger.info(f"Downloaded dataset to {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to pull dataset: {e}")
            return None
    
    def _save_dataset_locally(
        self,
        dataset_path: str,
        repo_id: str,
        dataset_card: Optional[DatasetCard] = None,
    ) -> Dict[str, Any]:
        """Save dataset to local storage."""
        import shutil
        
        local_path = self.local_cache_dir / "datasets" / repo_id.replace("/", "_")
        local_path.mkdir(parents=True, exist_ok=True)
        
        src = Path(dataset_path)
        if src.is_dir():
            for item in src.iterdir():
                if item.is_file():
                    shutil.copy2(item, local_path / item.name)
        elif src.is_file():
            shutil.copy2(src, local_path / src.name)
        
        if dataset_card:
            with open(local_path / "README.md", "w") as f:
                f.write(dataset_card.to_markdown())
        
        return {
            "success": True,
            "local_path": str(local_path),
            "storage": "local",
        }
    
    # =========================================================================
    # Model Card Generation
    # =========================================================================
    
    def create_model_card(
        self,
        model_name: str,
        base_model: str,
        description: str,
        training_method: str = "",
        training_dataset: str = "",
        metrics: Optional[Dict[str, float]] = None,
        tags: Optional[List[str]] = None,
    ) -> ModelCard:
        """
        Create a model card.
        
        Args:
            model_name: Name of the model
            base_model: Base model used
            description: Model description
            training_method: Training method (lora, full, etc.)
            training_dataset: Dataset used for training
            metrics: Performance metrics
            tags: Model tags
        
        Returns:
            ModelCard instance
        """
        default_tags = ["text-generation", "custom-model"]
        if training_method:
            default_tags.append(training_method.lower())
        
        return ModelCard(
            model_name=model_name,
            base_model=base_model,
            description=description,
            training_method=training_method,
            training_framework="agentic-assistants",
            training_dataset=training_dataset,
            metrics=metrics or {},
            tags=(tags or []) + default_tags,
        )
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def list_models(
        self,
        author: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List models from HuggingFace Hub."""
        if not self._hub_available:
            return []
        
        try:
            from huggingface_hub import HfApi
            
            api = HfApi(token=self.token)
            
            models = api.list_models(
                author=author,
                search=search,
                limit=limit,
            )
            
            return [
                {
                    "id": m.id,
                    "author": m.author,
                    "downloads": m.downloads,
                    "likes": m.likes,
                    "tags": m.tags,
                }
                for m in models
            ]
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def model_exists(self, repo_id: str) -> bool:
        """Check if a model exists on the Hub."""
        if not self._hub_available:
            return False
        
        try:
            from huggingface_hub import HfApi
            
            api = HfApi(token=self.token)
            api.model_info(repo_id)
            return True
        except Exception:
            return False
    
    def get_model_info(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        if not self._hub_available:
            return None
        
        try:
            from huggingface_hub import HfApi
            
            api = HfApi(token=self.token)
            info = api.model_info(repo_id)
            
            return {
                "id": info.id,
                "author": info.author,
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "created_at": str(info.created_at) if info.created_at else None,
                "last_modified": str(info.last_modified) if info.last_modified else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
    
    def get_storage_backend(self) -> str:
        """Get the current storage backend."""
        if self.is_available:
            return "huggingface_hub"
        return "local"
