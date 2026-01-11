"""
Jupyter integration with magic commands for catalog and pipeline interaction.

This module provides IPython magic commands for working with the data catalog
and pipelines from within Jupyter notebooks.

Available magics:
- %reload_catalog - Reload the catalog from YAML
- %run_pipeline - Execute a pipeline
- %load_node - Load node outputs interactively
- %catalog_browser - Interactive catalog browser widget
- %show_pipeline - Visualize a pipeline DAG

Example:
    >>> # In a Jupyter notebook:
    >>> %load_ext agentic_assistants.integrations.jupyter
    >>> 
    >>> # Reload catalog
    >>> %reload_catalog conf/base/catalog.yaml
    >>> 
    >>> # Run a pipeline
    >>> %run_pipeline data_processing
    >>> 
    >>> # Load a dataset
    >>> df = %load_dataset users
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# Check for IPython
try:
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
    from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
    from IPython import get_ipython
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False
    Magics = object
    
    def magics_class(cls):
        return cls
    
    def line_magic(func):
        return func
    
    def cell_magic(func):
        return func
    
    def magic_arguments(func):
        return func
    
    def argument(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def parse_argstring(magic_func, line):
        return None


# Global state for the magic commands
_catalog = None
_pipeline_registry = None


def _get_catalog():
    """Get or create the global catalog."""
    global _catalog
    if _catalog is None:
        from agentic_assistants.data.catalog import DataCatalog
        _catalog = DataCatalog()
    return _catalog


def _set_catalog(catalog):
    """Set the global catalog."""
    global _catalog
    _catalog = catalog


def _get_registry():
    """Get or create the global pipeline registry."""
    global _pipeline_registry
    if _pipeline_registry is None:
        from agentic_assistants.pipelines.registry import get_pipeline_registry
        _pipeline_registry = get_pipeline_registry()
    return _pipeline_registry


if HAS_IPYTHON:
    @magics_class
    class AgenticMagics(Magics):
        """
        IPython magic commands for Agentic framework integration.
        
        Provides convenient shortcuts for working with the data catalog
        and pipeline system from Jupyter notebooks.
        """
        
        @line_magic
        @magic_arguments()
        @argument('path', nargs='?', default=None, help='Path to catalog.yaml')
        @argument('-e', '--env', default='base', help='Environment name')
        def reload_catalog(self, line):
            """
            Reload the data catalog from YAML configuration.
            
            Usage:
                %reload_catalog [path] [-e env]
                
            Examples:
                %reload_catalog
                %reload_catalog conf/base/catalog.yaml
                %reload_catalog -e local
            """
            args = parse_argstring(self.reload_catalog, line)
            
            from agentic_assistants.data.catalog import DataCatalog
            
            if args.path:
                catalog = DataCatalog.from_yaml(args.path)
            else:
                # Try to find config directory
                for conf_dir in ['conf', 'config', '.']:
                    conf_path = Path(conf_dir)
                    if conf_path.exists():
                        catalog = DataCatalog.from_config_dir(conf_path, env=args.env)
                        break
                else:
                    print("No configuration directory found. Creating empty catalog.")
                    catalog = DataCatalog()
            
            _set_catalog(catalog)
            print(f"Catalog loaded with {len(catalog.list_datasets())} datasets")
            return catalog
        
        @line_magic
        @magic_arguments()
        @argument('name', help='Dataset name to load')
        @argument('-v', '--version', default=None, help='Specific version to load')
        def load_dataset(self, line):
            """
            Load a dataset from the catalog.
            
            Usage:
                %load_dataset name [-v version]
                
            Examples:
                %load_dataset users
                %load_dataset processed_data -v 2024-01-15T10.30.00.000000Z
            """
            args = parse_argstring(self.load_dataset, line)
            
            catalog = _get_catalog()
            data = catalog.load(args.name, version=args.version)
            
            # Display info about the loaded data
            if hasattr(data, 'shape'):
                print(f"Loaded '{args.name}': {data.shape}")
            elif hasattr(data, '__len__'):
                print(f"Loaded '{args.name}': {len(data)} items")
            else:
                print(f"Loaded '{args.name}'")
            
            return data
        
        @line_magic
        @magic_arguments()
        @argument('name', help='Pipeline name to run')
        @argument('-r', '--runner', default='sequential', help='Runner type')
        @argument('--from-nodes', nargs='*', help='Start from these nodes')
        @argument('--to-nodes', nargs='*', help='Run up to these nodes')
        @argument('--tags', nargs='*', help='Filter by tags')
        def run_pipeline(self, line):
            """
            Execute a pipeline.
            
            Usage:
                %run_pipeline name [-r runner] [--from-nodes ...] [--to-nodes ...] [--tags ...]
                
            Examples:
                %run_pipeline data_processing
                %run_pipeline training -r parallel
                %run_pipeline training --tags preprocessing feature_engineering
            """
            args = parse_argstring(self.run_pipeline, line)
            
            registry = _get_registry()
            catalog = _get_catalog()
            
            # Get pipeline
            pipeline = registry.get(args.name)
            if pipeline is None:
                print(f"Pipeline '{args.name}' not found")
                return None
            
            # Apply filters
            if args.from_nodes:
                pipeline = pipeline.from_nodes(*args.from_nodes)
            if args.to_nodes:
                pipeline = pipeline.to_nodes(*args.to_nodes)
            if args.tags:
                pipeline = pipeline.only_nodes_with_tags(*args.tags)
            
            # Get runner
            if args.runner == 'parallel':
                from agentic_assistants.pipelines.runners import ParallelRunner
                runner = ParallelRunner()
            elif args.runner == 'thread':
                from agentic_assistants.pipelines.runners import ThreadRunner
                runner = ThreadRunner()
            else:
                from agentic_assistants.pipelines.runners import SequentialRunner
                runner = SequentialRunner()
            
            # Run
            print(f"Running pipeline '{args.name}' with {len(pipeline)} nodes...")
            result = runner.run(pipeline, catalog)
            
            if result.success:
                print(f"✓ Pipeline completed in {result.duration_seconds:.2f}s")
            else:
                print(f"✗ Pipeline failed: {result.errors}")
            
            return result
        
        @line_magic
        @magic_arguments()
        @argument('name', nargs='?', default=None, help='Pipeline name to visualize')
        def show_pipeline(self, line):
            """
            Display a pipeline visualization.
            
            Usage:
                %show_pipeline [name]
                
            Examples:
                %show_pipeline
                %show_pipeline data_processing
            """
            args = parse_argstring(self.show_pipeline, line)
            
            registry = _get_registry()
            
            if args.name:
                pipeline = registry.get(args.name)
            else:
                pipeline = registry.get_default_pipeline()
            
            if pipeline is None:
                print("No pipeline to visualize")
                return
            
            # Try to use graphviz for visualization
            try:
                from IPython.display import SVG, display
                svg = _create_pipeline_svg(pipeline)
                if svg:
                    display(SVG(svg))
                    return
            except ImportError:
                pass
            
            # Fall back to text representation
            print(pipeline.describe())
        
        @line_magic
        def list_datasets(self, line):
            """
            List all datasets in the catalog.
            
            Usage:
                %list_datasets
            """
            catalog = _get_catalog()
            datasets = catalog.list_datasets()
            
            if not datasets:
                print("No datasets in catalog")
                return []
            
            print(f"Datasets ({len(datasets)}):")
            for name in sorted(datasets):
                config = catalog.get_dataset_config(name)
                type_str = config.type if config else "unknown"
                print(f"  - {name} ({type_str})")
            
            return datasets
        
        @line_magic
        def list_pipelines(self, line):
            """
            List all registered pipelines.
            
            Usage:
                %list_pipelines
            """
            registry = _get_registry()
            pipelines = registry.list_pipelines()
            
            if not pipelines:
                print("No registered pipelines")
                return []
            
            print(f"Pipelines ({len(pipelines)}):")
            for name in sorted(pipelines):
                pipe = registry.get(name)
                if pipe:
                    print(f"  - {name} ({len(pipe)} nodes)")
            
            return pipelines
        
        @line_magic
        @magic_arguments()
        @argument('query', nargs='?', default='', help='Search query')
        @argument('-t', '--type', default=None, help='Filter by type')
        def search_catalog(self, line):
            """
            Search the data catalog.
            
            Usage:
                %search_catalog [query] [-t type]
                
            Examples:
                %search_catalog user
                %search_catalog -t table
            """
            args = parse_argstring(self.search_catalog, line)
            
            catalog = _get_catalog()
            results = catalog.search(args.query, entity_type=args.type)
            
            if not results.entries:
                print("No results found")
                return results
            
            print(f"Found {results.total} results:")
            for entry in results.entries[:20]:  # Limit display
                print(f"  - {entry.name} ({entry.entry_type})")
            
            if results.total > 20:
                print(f"  ... and {results.total - 20} more")
            
            return results
        
        @cell_magic
        def save_dataset(self, line, cell):
            """
            Save data to a dataset.
            
            Usage:
                %%save_dataset name
                data = ...
                
            The cell should produce a value to save.
            """
            parts = line.strip().split()
            if not parts:
                print("Usage: %%save_dataset dataset_name")
                return
            
            name = parts[0]
            
            # Execute the cell
            result = self.shell.run_cell(cell)
            
            if result.error_in_exec:
                print(f"Error executing cell: {result.error_in_exec}")
                return
            
            # Save the result
            data = result.result
            if data is None:
                print("No data to save (cell returned None)")
                return
            
            catalog = _get_catalog()
            catalog.save(name, data)
            print(f"Saved '{name}'")


def _create_pipeline_svg(pipeline) -> Optional[str]:
    """Create an SVG visualization of a pipeline."""
    try:
        import graphviz
    except ImportError:
        return None
    
    dot = graphviz.Digraph(comment='Pipeline')
    dot.attr(rankdir='LR')
    
    # Add input nodes
    for input_name in pipeline.inputs:
        dot.node(input_name, input_name, shape='ellipse', style='filled', fillcolor='lightblue')
    
    # Add nodes
    for node in pipeline.nodes:
        dot.node(node.name, node.name, shape='box', style='filled', fillcolor='lightgreen')
        
        # Connect inputs
        for input_name in node.input_names:
            dot.edge(input_name, node.name)
        
        # Connect outputs
        for output_name in node.output_names:
            if output_name not in pipeline.outputs:
                dot.node(output_name, output_name, shape='ellipse', style='dashed')
            else:
                dot.node(output_name, output_name, shape='ellipse', style='filled', fillcolor='lightyellow')
            dot.edge(node.name, output_name)
    
    return dot.pipe(format='svg').decode('utf-8')


def load_ipython_extension(ipython):
    """
    Load the IPython extension.
    
    This function is called by IPython when you run:
        %load_ext agentic_assistants.integrations.jupyter
    """
    ipython.register_magics(AgenticMagics)
    print("Agentic magic commands loaded. Use %reload_catalog to get started.")


def unload_ipython_extension(ipython):
    """Unload the IPython extension."""
    pass


# Standalone functions for use without magics
def setup_notebook_environment(
    catalog_path: Optional[str] = None,
    env: str = "base",
) -> Dict[str, Any]:
    """
    Set up the notebook environment for agentic development.
        
        Args:
        catalog_path: Path to catalog.yaml
        env: Environment name
        
        Returns:
        Dictionary with catalog and registry
    """
    from agentic_assistants.data.catalog import DataCatalog
    from agentic_assistants.pipelines.registry import get_pipeline_registry
    
    if catalog_path:
        catalog = DataCatalog.from_yaml(catalog_path)
    else:
        # Try to find config
        for conf_dir in ['conf', 'config', '.']:
            conf_path = Path(conf_dir)
            if conf_path.exists():
                catalog = DataCatalog.from_config_dir(conf_path, env=env)
                break
        else:
            catalog = DataCatalog()
    
    _set_catalog(catalog)
    
    registry = get_pipeline_registry()
    
    return {
        "catalog": catalog,
        "registry": registry,
    }


def display_dataframe_info(df: Any, name: str = "DataFrame") -> None:
    """
    Display rich information about a DataFrame in Jupyter.
    
    Args:
        df: pandas DataFrame
        name: Display name
    """
    try:
        from IPython.display import display, HTML
        import pandas as pd
        
        if not isinstance(df, pd.DataFrame):
            print(f"{name} is not a DataFrame")
            return
        
        html = f"""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0;">
            <h4>{name}</h4>
            <p><strong>Shape:</strong> {df.shape[0]} rows × {df.shape[1]} columns</p>
            <p><strong>Memory:</strong> {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB</p>
            <p><strong>Columns:</strong> {', '.join(df.columns[:10])}{' ...' if len(df.columns) > 10 else ''}</p>
        </div>
        """
        display(HTML(html))
        
    except ImportError:
        print(f"{name}: {df.shape if hasattr(df, 'shape') else 'unknown shape'}")


# Widget-based catalog browser (requires ipywidgets)
def create_catalog_browser() -> Optional[Any]:
    """
    Create an interactive catalog browser widget.
    
    Returns:
        ipywidgets widget or None if not available
    """
    try:
        import ipywidgets as widgets
        from IPython.display import display
    except ImportError:
        print("ipywidgets not installed. Install with: pip install ipywidgets")
        return None
    
    catalog = _get_catalog()
    datasets = catalog.list_datasets()
    
    # Create dropdown
    dropdown = widgets.Dropdown(
        options=[''] + sorted(datasets),
        description='Dataset:',
        disabled=False,
    )
    
    # Output area
    output = widgets.Output()
    
    def on_change(change):
        with output:
            output.clear_output()
            if change['new']:
                try:
                    data = catalog.load(change['new'])
                    if hasattr(data, 'head'):
                        display(data.head())
                    else:
                        print(f"Loaded: {type(data)}")
                except Exception as e:
                    print(f"Error loading: {e}")
    
    dropdown.observe(on_change, names='value')
    
    # Layout
    box = widgets.VBox([
        widgets.HTML('<h3>Catalog Browser</h3>'),
        dropdown,
        output,
    ])
    
    return box
