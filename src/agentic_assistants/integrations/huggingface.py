"""
HuggingFace Hub integration.

This module provides integration with HuggingFace Hub for:
- Model storage and versioning
- Dataset hosting and loading
- Model cards generation
- Inference API integration
- Paper search and retrieval
- LoRA adapter weight management
- Model/tokenizer loading via transformers
- Spaces listing

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
    >>>
    >>> # Load a model and tokenizer via transformers
    >>> model, tokenizer = hf.load_model_and_tokenizer("meta-llama/Llama-3.2-1B")
    >>>
    >>> # Search papers
    >>> papers = hf.search_papers("reinforcement learning")
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

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

    def set_token(self, token: Optional[str]) -> None:
        """Update the API token and re-check Hub availability."""
        self.token = token
        self._hub_available = self._check_hub()

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

    # =========================================================================
    # Authentication
    # =========================================================================

    def whoami(self) -> Optional[Dict[str, Any]]:
        """Get current user info from HuggingFace Hub."""
        if not self._hub_available or not self.token:
            return None

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)
            info = api.whoami()
            return {
                "name": info.get("name"),
                "fullname": info.get("fullname"),
                "email": info.get("email"),
                "orgs": [
                    {"name": org.get("name"), "id": org.get("id")}
                    for org in info.get("orgs", [])
                ],
                "auth": info.get("auth", {}),
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None

    def login(self, token: str) -> bool:
        """Validate and set a new HuggingFace token."""
        old_token = self.token
        self.token = token
        self._hub_available = self._check_hub()

        if self.whoami() is not None:
            return True

        self.token = old_token
        self._hub_available = self._check_hub()
        return False

    # =========================================================================
    # Paper Operations
    # =========================================================================

    def search_papers(
        self,
        query: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search papers on HuggingFace via the Hub API.

        Args:
            query: Search query string
            limit: Maximum papers to return

        Returns:
            List of paper metadata dicts
        """
        if not self._hub_available:
            return []

        try:
            import httpx

            response = httpx.get(
                f"{self._hub_url}/api/papers",
                params={"query": query, "limit": limit},
                headers=self._auth_headers(),
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Paper search returned {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Failed to search papers: {e}")
            return []

    def get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific paper by its arXiv ID or HF paper ID.

        Args:
            paper_id: Paper identifier (e.g. "2305.18290")

        Returns:
            Paper metadata or None
        """
        if not self._hub_available:
            return None

        try:
            import httpx

            response = httpx.get(
                f"{self._hub_url}/api/papers/{paper_id}",
                headers=self._auth_headers(),
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get paper: {e}")
            return None

    # =========================================================================
    # Weight Operations (LoRA adapters)
    # =========================================================================

    def push_weights(
        self,
        weights_path: str,
        repo_id: str,
        adapter_name: str = "default",
        private: bool = False,
        commit_message: str = "Upload adapter weights",
    ) -> Dict[str, Any]:
        """
        Push LoRA/PEFT adapter weights to HuggingFace Hub.

        Args:
            weights_path: Local path to adapter weights directory
            repo_id: HuggingFace repo ID
            adapter_name: Name for this adapter variant
            private: Make repo private
            commit_message: Commit message

        Returns:
            Result dictionary
        """
        if not self.is_available:
            if self.default_to_local:
                return self._save_model_locally(weights_path, repo_id, None)
            return {"success": False, "error": "HuggingFace Hub not available"}

        try:
            from huggingface_hub import HfApi, create_repo

            api = HfApi(token=self.token)

            create_repo(repo_id, token=self.token, private=private, exist_ok=True)

            path_in_repo = adapter_name if adapter_name != "default" else ""

            api.upload_folder(
                folder_path=weights_path,
                repo_id=repo_id,
                path_in_repo=path_in_repo,
                commit_message=commit_message,
            )

            url = f"https://huggingface.co/{repo_id}"
            logger.info(f"Pushed adapter weights to {url}")

            return {
                "success": True,
                "repo_id": repo_id,
                "adapter_name": adapter_name,
                "url": url,
            }
        except Exception as e:
            logger.error(f"Failed to push weights: {e}")
            if self.default_to_local:
                return self._save_model_locally(weights_path, repo_id, None)
            return {"success": False, "error": str(e)}

    def pull_weights(
        self,
        repo_id: str,
        adapter_name: str = "default",
        revision: Optional[str] = None,
        local_dir: Optional[str] = None,
    ) -> Optional[str]:
        """
        Pull LoRA/PEFT adapter weights from HuggingFace Hub.

        Args:
            repo_id: HuggingFace repo ID
            adapter_name: Name of the adapter variant
            revision: Specific revision
            local_dir: Local directory to save to

        Returns:
            Local path to downloaded weights
        """
        if not self._hub_available:
            local_path = self.local_cache_dir / "weights" / repo_id.replace("/", "_")
            if local_path.exists():
                return str(local_path)
            return None

        try:
            from huggingface_hub import snapshot_download

            local_dir = local_dir or str(
                self.local_cache_dir / "weights" / repo_id.replace("/", "_")
            )

            allow_patterns = None
            if adapter_name != "default":
                allow_patterns = [f"{adapter_name}/*", f"{adapter_name}/**"]

            path = snapshot_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=local_dir,
                token=self.token,
                allow_patterns=allow_patterns,
            )

            logger.info(f"Downloaded adapter weights to {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to pull weights: {e}")
            return None

    # =========================================================================
    # Dataset Operations (extended)
    # =========================================================================

    def load_hf_dataset(
        self,
        dataset_id: str,
        split: Optional[str] = None,
        subset: Optional[str] = None,
        streaming: bool = False,
    ) -> Any:
        """
        Load a dataset using the HuggingFace datasets library.

        Args:
            dataset_id: HuggingFace dataset ID or local path
            split: Dataset split (train, test, validation)
            subset: Dataset subset/configuration name
            streaming: Enable streaming mode for large datasets

        Returns:
            HuggingFace Dataset or DatasetDict object

        Raises:
            ImportError: If datasets library is not installed
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "datasets library required. Install with: pip install datasets"
            )

        kwargs: Dict[str, Any] = {"streaming": streaming}
        if split:
            kwargs["split"] = split
        if subset:
            kwargs["name"] = subset
        if self.token:
            kwargs["token"] = self.token

        return load_dataset(dataset_id, **kwargs)

    def list_datasets(
        self,
        author: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List datasets from HuggingFace Hub."""
        if not self._hub_available:
            return []

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)

            datasets = api.list_datasets(
                author=author,
                search=search,
                limit=limit,
            )

            return [
                {
                    "id": d.id,
                    "author": d.author,
                    "downloads": d.downloads,
                    "likes": d.likes,
                    "tags": d.tags,
                }
                for d in datasets
            ]
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []

    def get_dataset_info(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a dataset on the Hub."""
        if not self._hub_available:
            return None

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)
            info = api.dataset_info(repo_id)

            return {
                "id": info.id,
                "author": info.author,
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "description": info.description,
                "created_at": str(info.created_at) if info.created_at else None,
                "last_modified": str(info.last_modified) if info.last_modified else None,
            }
        except Exception as e:
            logger.error(f"Failed to get dataset info: {e}")
            return None

    # =========================================================================
    # Model Loading (via transformers)
    # =========================================================================

    def load_model(
        self,
        model_id: str,
        device_map: Optional[str] = "auto",
        torch_dtype: Optional[str] = None,
        quantization_config: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """
        Load a model using transformers AutoModel.

        Args:
            model_id: HuggingFace model ID or local path
            device_map: Device mapping strategy
            torch_dtype: Torch dtype string (e.g. "bfloat16", "float16")
            quantization_config: BitsAndBytes or GPTQ quantization config
            **kwargs: Additional arguments for from_pretrained

        Returns:
            Loaded model

        Raises:
            ImportError: If transformers is not installed
        """
        try:
            from transformers import AutoModelForCausalLM
        except ImportError:
            raise ImportError(
                "transformers library required. Install with: pip install transformers"
            )

        load_kwargs: Dict[str, Any] = {**kwargs}
        if device_map:
            load_kwargs["device_map"] = device_map
        if torch_dtype:
            import torch
            dtype_map = {
                "bfloat16": torch.bfloat16,
                "float16": torch.float16,
                "float32": torch.float32,
            }
            load_kwargs["torch_dtype"] = dtype_map.get(torch_dtype, torch.float32)
        if quantization_config:
            load_kwargs["quantization_config"] = quantization_config
        if self.token:
            load_kwargs["token"] = self.token

        logger.info(f"Loading model {model_id}")
        return AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)

    def load_tokenizer(self, model_id: str, **kwargs) -> Any:
        """
        Load a tokenizer using transformers AutoTokenizer.

        Args:
            model_id: HuggingFace model ID or local path
            **kwargs: Additional arguments for from_pretrained

        Returns:
            Loaded tokenizer

        Raises:
            ImportError: If transformers is not installed
        """
        try:
            from transformers import AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers library required. Install with: pip install transformers"
            )

        load_kwargs: Dict[str, Any] = {**kwargs}
        if self.token:
            load_kwargs["token"] = self.token

        tokenizer = AutoTokenizer.from_pretrained(model_id, **load_kwargs)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        return tokenizer

    def load_model_and_tokenizer(
        self,
        model_id: str,
        device_map: Optional[str] = "auto",
        torch_dtype: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Any, Any]:
        """
        Load both model and tokenizer.

        Returns:
            Tuple of (model, tokenizer)
        """
        model = self.load_model(model_id, device_map=device_map, torch_dtype=torch_dtype, **kwargs)
        tokenizer = self.load_tokenizer(model_id)
        return model, tokenizer

    def search_models(
        self,
        query: Optional[str] = None,
        author: Optional[str] = None,
        task: Optional[str] = None,
        library: Optional[str] = None,
        language: Optional[str] = None,
        sort: str = "downloads",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search models on HuggingFace Hub with advanced filters.

        The ``task``, ``library``, and ``language`` filters are applied
        client-side for compatibility with huggingface_hub v1.0+ which
        removed those keyword arguments from ``HfApi.list_models()``.

        Args:
            query: Search query
            author: Filter by author/org
            task: Filter by task (text-generation, text-classification, etc.)
            library: Filter by library (pytorch, tensorflow, etc.)
            language: Filter by language
            sort: Sort field (downloads, likes, created_at, etc.)
            limit: Maximum results

        Returns:
            List of model info dicts
        """
        if not self._hub_available:
            return []

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)

            needs_filtering = bool(task or library or language)
            fetch_limit = limit * 3 if needs_filtering else limit

            models = api.list_models(
                search=query,
                author=author,
                sort=sort,
                limit=fetch_limit,
            )

            results: List[Dict[str, Any]] = []
            for m in models:
                if task and getattr(m, "pipeline_tag", None) != task:
                    continue
                if library and library not in (getattr(m, "tags", None) or []):
                    lib_name = getattr(m, "library_name", None)
                    if lib_name != library:
                        continue
                if language and language not in (getattr(m, "tags", None) or []):
                    continue

                results.append({
                    "id": m.id,
                    "author": m.author,
                    "downloads": m.downloads,
                    "likes": m.likes,
                    "tags": m.tags,
                    "pipeline_tag": getattr(m, "pipeline_tag", None),
                    "library_name": getattr(m, "library_name", None),
                    "created_at": str(m.created_at) if getattr(m, "created_at", None) else None,
                    "last_modified": str(m.last_modified) if getattr(m, "last_modified", None) else None,
                })
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            logger.error(f"Failed to search models: {e}")
            return []

    # =========================================================================
    # Spaces
    # =========================================================================

    def list_spaces(
        self,
        author: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List Spaces from HuggingFace Hub."""
        if not self._hub_available:
            return []

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)

            spaces = api.list_spaces(
                author=author,
                search=search,
                limit=limit,
            )

            return [
                {
                    "id": s.id,
                    "author": s.author,
                    "likes": s.likes,
                    "sdk": getattr(s, "sdk", None),
                }
                for s in spaces
            ]
        except Exception as e:
            logger.error(f"Failed to list spaces: {e}")
            return []

    def get_space_info(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get info about a Space."""
        if not self._hub_available:
            return None

        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)
            info = api.space_info(repo_id)

            return {
                "id": info.id,
                "author": info.author,
                "likes": info.likes,
                "sdk": getattr(info, "sdk", None),
                "runtime": getattr(info, "runtime", None),
                "created_at": str(info.created_at) if getattr(info, "created_at", None) else None,
                "last_modified": str(info.last_modified) if getattr(info, "last_modified", None) else None,
            }
        except Exception as e:
            logger.error(f"Failed to get space info: {e}")
            return None

    # =========================================================================
    # Single-File Download
    # =========================================================================

    def download_file(
        self,
        repo_id: str,
        filename: str,
        repo_type: str = "model",
        revision: Optional[str] = None,
        local_dir: Optional[str] = None,
    ) -> Optional[str]:
        """
        Download a single file from a HuggingFace Hub repository.

        Unlike ``pull_model`` which fetches full snapshots, this retrieves one
        file (e.g. a README, config, or paper PDF).

        Args:
            repo_id: HuggingFace repo ID (e.g. "nvidia/Llama-3.1-Nemotron-Nano-8B-v1")
            filename: Path of the file inside the repo (e.g. "config.json")
            repo_type: Repository type -- "model", "dataset", or "space"
            revision: Specific revision/branch (default: main)
            local_dir: Directory to save the file into (defaults to cache dir)

        Returns:
            Absolute local path to the downloaded file, or None on failure
        """
        if not self._hub_available:
            logger.warning("HuggingFace Hub not available for file download")
            return None

        try:
            from huggingface_hub import hf_hub_download

            local_dir = local_dir or str(
                self.local_cache_dir / "files" / repo_id.replace("/", "_")
            )

            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                repo_type=repo_type if repo_type != "model" else None,
                revision=revision,
                local_dir=local_dir,
                token=self.token,
            )

            logger.info(f"Downloaded {filename} from {repo_id} to {path}")
            return path

        except Exception as e:
            logger.error(f"Failed to download file {filename} from {repo_id}: {e}")
            return None

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    @property
    def _hub_url(self) -> str:
        return os.environ.get("HF_HUB_URL", "https://huggingface.co")

    def _auth_headers(self) -> Dict[str, str]:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
