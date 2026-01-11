"""
OmegaConf-based configuration loader with environment support.

This module provides Kedro-style configuration loading with:
- Variable interpolation (${var} syntax)
- Environment-specific configs (base/local/staging/production)
- Credential resolution
- Environment variable integration

Example:
    >>> from agentic_assistants.config.loader import OmegaConfigLoader
    >>> 
    >>> loader = OmegaConfigLoader(conf_source="conf", env="local")
    >>> catalog = loader.get("catalog")
    >>> parameters = loader.get("parameters")
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import re

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# Try to import omegaconf, fall back to basic YAML if not available
try:
    from omegaconf import OmegaConf, DictConfig, ListConfig
    HAS_OMEGACONF = True
except ImportError:
    HAS_OMEGACONF = False
    logger.debug("omegaconf not installed, using basic YAML loading")

import yaml


class ConfigLoaderError(Exception):
    """Exception raised for configuration loading errors."""
    pass


def _resolve_env_var(value: str) -> str:
    """
    Resolve environment variable references in a string.
    
    Supports syntax:
    - ${env:VAR_NAME} - Get env var, error if not set
    - ${env:VAR_NAME,default} - Get env var with default value
    """
    pattern = r'\$\{env:([^,}]+)(?:,([^}]*))?\}'
    
    def replacer(match):
        var_name = match.group(1)
        default = match.group(2)
        
        value = os.environ.get(var_name)
        if value is None:
            if default is not None:
                return default
            raise ConfigLoaderError(
                f"Environment variable '{var_name}' not set and no default provided"
            )
        return value
    
    return re.sub(pattern, replacer, value)


def _resolve_globals(value: str, globals_dict: Dict[str, Any]) -> str:
    """
    Resolve global variable references in a string.
    
    Supports syntax:
    - ${globals:key} - Get value from globals
    """
    pattern = r'\$\{globals:([^}]+)\}'
    
    def replacer(match):
        key = match.group(1)
        if key not in globals_dict:
            raise ConfigLoaderError(f"Global '{key}' not defined")
        return str(globals_dict[key])
    
    return re.sub(pattern, replacer, value)


def _deep_resolve(
    config: Any,
    globals_dict: Dict[str, Any],
    resolve_env: bool = True,
) -> Any:
    """Recursively resolve interpolations in config."""
    if isinstance(config, dict):
        return {
            k: _deep_resolve(v, globals_dict, resolve_env)
            for k, v in config.items()
        }
    elif isinstance(config, list):
        return [_deep_resolve(v, globals_dict, resolve_env) for v in config]
    elif isinstance(config, str):
        result = config
        if resolve_env:
            result = _resolve_env_var(result)
        result = _resolve_globals(result, globals_dict)
        return result
    else:
        return config


class OmegaConfigLoader:
    """
    Kedro-style configuration loader with environment support.
    
    Loads configurations from a structured directory:
    ```
    conf/
      base/           # Shared configuration
        catalog.yaml
        parameters.yaml
        globals.yaml
      local/          # Local development overrides
        credentials.yaml
      staging/        # Staging environment
      production/     # Production settings
    ```
    
    Features:
    - Environment-specific config merging
    - Variable interpolation (${var} syntax)
    - Environment variable resolution (${env:VAR})
    - Globals for shared values (${globals:key})
    - Credential handling
    
    Example:
        >>> loader = OmegaConfigLoader(conf_source="conf", env="local")
        >>> 
        >>> # Get configuration sections
        >>> catalog = loader.get("catalog")
        >>> params = loader.get("parameters")
        >>> 
        >>> # Get credentials (typically gitignored)
        >>> creds = loader.get("credentials")
    """
    
    # Config types that are loaded
    CONFIG_PATTERNS = {
        "catalog": ["catalog.yaml", "catalog.yml", "catalog/**/*.yaml", "catalog/**/*.yml"],
        "parameters": ["parameters.yaml", "parameters.yml", "parameters/**/*.yaml", "parameters/**/*.yml"],
        "credentials": ["credentials.yaml", "credentials.yml"],
        "globals": ["globals.yaml", "globals.yml"],
        "logging": ["logging.yaml", "logging.yml"],
    }
    
    def __init__(
        self,
        conf_source: Union[str, Path],
        env: str = "base",
        runtime_params: Optional[Dict[str, Any]] = None,
        extra_environments: Optional[List[str]] = None,
    ):
        """
        Initialize the configuration loader.
        
        Args:
            conf_source: Path to the configuration directory
            env: Environment name (e.g., 'local', 'staging', 'production')
            runtime_params: Runtime parameters to override config
            extra_environments: Additional environments to load
        """
        self.conf_source = Path(conf_source)
        self.env = env
        self.runtime_params = runtime_params or {}
        self.extra_environments = extra_environments or []
        
        # Cache for loaded configs
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Load globals first for interpolation
        self._globals = self._load_globals()
        
        logger.info(f"ConfigLoader initialized for env='{env}'")
    
    def _load_globals(self) -> Dict[str, Any]:
        """Load globals from all environments."""
        globals_dict = {}
        
        for env in self._get_environment_order():
            env_path = self.conf_source / env
            if not env_path.exists():
                continue
            
            for pattern in self.CONFIG_PATTERNS.get("globals", []):
                for config_file in env_path.glob(pattern):
                    with open(config_file, "r") as f:
                        data = yaml.safe_load(f) or {}
                    globals_dict = self._merge_dicts(globals_dict, data)
        
        return globals_dict
    
    def _get_environment_order(self) -> List[str]:
        """Get the order of environments to load (later overrides earlier)."""
        envs = ["base"]
        
        # Add extra environments
        for extra in self.extra_environments:
            if extra not in envs:
                envs.append(extra)
        
        # Add main environment last (highest priority)
        if self.env != "base" and self.env not in envs:
            envs.append(self.env)
        
        return envs
    
    def get(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a configuration section by key.
        
        Args:
            key: Configuration key (e.g., 'catalog', 'parameters')
            default: Default value if not found
            
        Returns:
            Configuration dictionary
        """
        if key in self._cache:
            return self._cache[key]
        
        if key not in self.CONFIG_PATTERNS:
            logger.warning(f"Unknown config key: {key}")
            return default or {}
        
        # Load and merge configs from all environments
        config = {}
        
        for env in self._get_environment_order():
            env_path = self.conf_source / env
            if not env_path.exists():
                continue
            
            for pattern in self.CONFIG_PATTERNS[key]:
                for config_file in env_path.glob(pattern):
                    logger.debug(f"Loading config: {config_file}")
                    
                    with open(config_file, "r") as f:
                        if HAS_OMEGACONF:
                            data = OmegaConf.load(f)
                            data = OmegaConf.to_container(data, resolve=True)
                        else:
                            data = yaml.safe_load(f) or {}
                    
                    config = self._merge_dicts(config, data)
        
        # Resolve interpolations
        config = _deep_resolve(config, self._globals)
        
        # Apply runtime overrides
        if key == "parameters" and self.runtime_params:
            config = self._merge_dicts(config, self.runtime_params)
        
        # Cache and return
        self._cache[key] = config
        return config
    
    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configuration sections.
        
        Returns:
            Dictionary mapping config keys to their values
        """
        return {key: self.get(key) for key in self.CONFIG_PATTERNS}
    
    def list_environments(self) -> List[str]:
        """List available environments."""
        envs = []
        
        for item in self.conf_source.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                envs.append(item.name)
        
        return sorted(envs)
    
    def reload(self) -> None:
        """Clear cache and reload configurations."""
        self._cache.clear()
        self._globals = self._load_globals()
        logger.info("Configuration cache cleared")
    
    def __repr__(self) -> str:
        return f"OmegaConfigLoader(conf_source={self.conf_source!r}, env={self.env!r})"


class ConfigTemplateLoader:
    """
    Load and render configuration templates with variable substitution.
    
    Example:
        >>> loader = ConfigTemplateLoader()
        >>> config = loader.load_template("template.yaml", {"name": "my_project"})
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the template loader.
        
        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = Path(template_dir) if template_dir else None
    
    def load_template(
        self,
        template_path: Union[str, Path],
        variables: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Load and render a YAML template.
        
        Args:
            template_path: Path to the template file
            variables: Variables for substitution
            
        Returns:
            Rendered configuration dictionary
        """
        if self.template_dir and not Path(template_path).is_absolute():
            template_path = self.template_dir / template_path
        
        with open(template_path, "r") as f:
            content = f.read()
        
        # Simple variable substitution
        for key, value in variables.items():
            content = content.replace(f"${{{key}}}", str(value))
            content = content.replace(f"${{{{ {key} }}}}", str(value))
        
        return yaml.safe_load(content) or {}
    
    def render_string(
        self,
        template: str,
        variables: Dict[str, Any],
    ) -> str:
        """
        Render a template string.
        
        Args:
            template: Template string
            variables: Variables for substitution
            
        Returns:
            Rendered string
        """
        result = template
        
        for key, value in variables.items():
            result = result.replace(f"${{{key}}}", str(value))
        
        return result


def create_default_config_structure(
    project_path: Union[str, Path],
    project_name: str = "agentic_project",
) -> None:
    """
    Create the default configuration directory structure.
    
    Creates:
    ```
    conf/
      base/
        catalog.yaml
        parameters.yaml
        globals.yaml
      local/
        credentials.yaml
    ```
    
    Args:
        project_path: Root path of the project
        project_name: Name of the project
    """
    project_path = Path(project_path)
    conf_path = project_path / "conf"
    
    # Create directories
    (conf_path / "base").mkdir(parents=True, exist_ok=True)
    (conf_path / "local").mkdir(parents=True, exist_ok=True)
    
    # Create base/catalog.yaml
    catalog_content = f"""# Data Catalog for {project_name}
# Define datasets here using Kedro-style configuration

# Example:
# raw_data:
#   type: pandas.CSVDataset
#   filepath: data/01_raw/data.csv
#   load_args:
#     encoding: utf-8

# processed_data:
#   type: pandas.ParquetDataset
#   filepath: data/02_intermediate/processed.parquet
#   versioned: true
"""
    
    # Create base/parameters.yaml
    parameters_content = f"""# Parameters for {project_name}
# Define project parameters here

# model:
#   learning_rate: 0.001
#   batch_size: 32
#   epochs: 100

# preprocessing:
#   test_size: 0.2
#   random_state: 42
"""
    
    # Create base/globals.yaml
    globals_content = f"""# Global configuration for {project_name}
# These values can be referenced using ${{globals:key}} syntax

project_name: {project_name}
data_dir: data
"""
    
    # Create local/credentials.yaml
    credentials_content = """# Credentials - DO NOT commit this file!
# Add this file to .gitignore

# database:
#   username: your_username
#   password: your_password
#   host: localhost
#   port: 5432

# api:
#   key: your_api_key
"""
    
    # Write files
    files = [
        (conf_path / "base" / "catalog.yaml", catalog_content),
        (conf_path / "base" / "parameters.yaml", parameters_content),
        (conf_path / "base" / "globals.yaml", globals_content),
        (conf_path / "local" / "credentials.yaml", credentials_content),
    ]
    
    for file_path, content in files:
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write(content)
            logger.info(f"Created: {file_path}")
        else:
            logger.debug(f"Skipped existing: {file_path}")
    
    logger.info(f"Configuration structure created at: {conf_path}")
