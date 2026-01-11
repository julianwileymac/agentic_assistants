"""
Hook manager for registering and calling hook implementations.

This module provides the HookManager class that coordinates hook
registration and invocation.

Example:
    >>> from agentic_assistants.hooks import HookManager
    >>> 
    >>> manager = HookManager()
    >>> manager.register(my_hook_implementation)
    >>> 
    >>> # Hooks are called automatically during pipeline/node/dataset operations
"""

from typing import Any, Dict, List, Optional, Type
import warnings

from agentic_assistants.hooks.specs import (
    PipelineHookSpec,
    NodeHookSpec,
    DatasetHookSpec,
    CatalogHookSpec,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Try to import pluggy
try:
    import pluggy
    HAS_PLUGGY = True
except ImportError:
    HAS_PLUGGY = False
    pluggy = None


class HookManager:
    """
    Manages hook registrations and invocations.
    
    The HookManager uses pluggy (if available) for hook management,
    falling back to a simple implementation if pluggy is not installed.
    
    Attributes:
        hook: Hook caller for invoking hooks
        
    Example:
        >>> manager = HookManager()
        >>> 
        >>> # Register a hook implementation
        >>> manager.register(MLFlowHook())
        >>> 
        >>> # Call hooks
        >>> manager.hook.before_pipeline_run(pipeline=pipe, catalog=cat)
    """
    
    PROJECT_NAME = "agentic"
    
    def __init__(self):
        """Initialize the hook manager."""
        self._hooks: List[Any] = []
        
        if HAS_PLUGGY:
            # Use pluggy for full hook management
            self._pm = pluggy.PluginManager(self.PROJECT_NAME)
            
            # Register hook specifications
            self._pm.add_hookspecs(PipelineHookSpec)
            self._pm.add_hookspecs(NodeHookSpec)
            self._pm.add_hookspecs(DatasetHookSpec)
            self._pm.add_hookspecs(CatalogHookSpec)
            
            self.hook = self._pm.hook
        else:
            # Use simple fallback
            self._pm = None
            self.hook = _SimpleHookCaller(self)
        
        logger.debug(f"HookManager initialized (pluggy={HAS_PLUGGY})")
    
    def register(self, hook_impl: Any, name: Optional[str] = None) -> None:
        """
        Register a hook implementation.
        
        Args:
            hook_impl: Object with hook implementation methods
            name: Optional name for the plugin
        """
        self._hooks.append(hook_impl)
        
        if self._pm:
            name = name or getattr(hook_impl, "__name__", None) or hook_impl.__class__.__name__
            self._pm.register(hook_impl, name=name)
        
        logger.info(f"Registered hook: {hook_impl.__class__.__name__}")
    
    def unregister(self, hook_impl: Any) -> None:
        """
        Unregister a hook implementation.
        
        Args:
            hook_impl: The hook implementation to remove
        """
        if hook_impl in self._hooks:
            self._hooks.remove(hook_impl)
        
        if self._pm:
            try:
                self._pm.unregister(hook_impl)
            except ValueError:
                pass
        
        logger.info(f"Unregistered hook: {hook_impl.__class__.__name__}")
    
    def list_hooks(self) -> List[str]:
        """List all registered hook implementations."""
        return [h.__class__.__name__ for h in self._hooks]
    
    def get_hooks(self) -> List[Any]:
        """Get all registered hook implementations."""
        return self._hooks.copy()
    
    def clear(self) -> None:
        """Remove all registered hooks."""
        for hook in self._hooks.copy():
            self.unregister(hook)
        self._hooks.clear()
    
    def is_registered(self, hook_impl: Any) -> bool:
        """Check if a hook is registered."""
        return hook_impl in self._hooks


class _SimpleHookCaller:
    """
    Simple hook caller fallback when pluggy is not available.
    
    Provides the same interface as pluggy's hook caller but with
    a simplified implementation.
    """
    
    def __init__(self, manager: HookManager):
        self._manager = manager
    
    def __getattr__(self, name: str):
        """Return a callable for any hook name."""
        def caller(**kwargs):
            results = []
            for hook in self._manager._hooks:
                if hasattr(hook, name):
                    try:
                        method = getattr(hook, name)
                        result = method(**kwargs)
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        logger.warning(f"Hook {name} failed in {hook.__class__.__name__}: {e}")
            return results
        return caller


# Global hook manager instance
_global_hook_manager: Optional[HookManager] = None


def get_hook_manager() -> HookManager:
    """Get the global hook manager."""
    global _global_hook_manager
    if _global_hook_manager is None:
        _global_hook_manager = HookManager()
    return _global_hook_manager


def set_hook_manager(manager: HookManager) -> None:
    """Set the global hook manager."""
    global _global_hook_manager
    _global_hook_manager = manager


def register_hook(hook_impl: Any) -> None:
    """
    Register a hook with the global hook manager.
    
    Convenience function for quick hook registration.
    
    Args:
        hook_impl: Hook implementation to register
    """
    get_hook_manager().register(hook_impl)
