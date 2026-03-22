"""
Composio integration for tool/API integrations.
"""

from typing import Any, Dict, List, Optional

try:
    from composio import ComposioToolSet
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ComposioAdapter:
    """
    Adapter for Composio tool integration platform.
    
    Features:
    - Pre-built actions for common services
    - Authentication management
    - Tool execution and monitoring
    - Integration with agent frameworks
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """Initialize Composio adapter."""
        if not COMPOSIO_AVAILABLE:
            raise ImportError("composio-core is required. Install with: pip install composio-core")
        
        import os
        
        self.config = config or AgenticConfig()
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")
        
        if not self.api_key:
            raise ValueError("Composio API key is required")
        
        self.toolset = ComposioToolSet(api_key=self.api_key)
        logger.info("Composio adapter initialized")
    
    def list_apps(self) -> List[Dict[str, Any]]:
        """
        List available apps/integrations.
        
        Returns:
            List of available apps
        """
        apps = self.toolset.get_apps()
        return apps
    
    def list_actions(self, app: str) -> List[Dict[str, Any]]:
        """
        List actions for an app.
        
        Args:
            app: App name
            
        Returns:
            List of actions
        """
        actions = self.toolset.get_actions(app=app)
        return actions
    
    def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an action.
        
        Args:
            action: Action identifier
            params: Action parameters
            entity_id: Optional entity ID for auth context
            
        Returns:
            Action result
        """
        logger.info(f"Executing Composio action: {action}")
        
        result = self.toolset.execute_action(
            action=action,
            params=params,
            entity_id=entity_id,
        )
        
        return result
    
    def get_tools_for_agent(
        self,
        app: str,
        framework: str = "crewai",
    ) -> List[Any]:
        """
        Get tools for an agent framework.
        
        Args:
            app: App name
            framework: Framework name (crewai, langchain, etc.)
            
        Returns:
            List of tools for the framework
        """
        tools = self.toolset.get_tools(apps=[app])
        return tools
