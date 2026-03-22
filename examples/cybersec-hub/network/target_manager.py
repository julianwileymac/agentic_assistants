"""
Target Management for Security Testing.

Manages authorized targets and scope for security assessments.
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import re
import ipaddress

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Target:
    """Authorized target."""
    target_id: str
    identifier: str  # IP, hostname, or CIDR
    description: str
    authorization_token: str
    authorized_by: str
    authorized_at: str
    expires_at: Optional[str]
    scope: List[str]  # Services/ports in scope
    out_of_scope: List[str]  # Explicitly excluded
    metadata: Dict[str, Any]


class TargetManager:
    """
    Manages authorized targets for security testing.
    
    Ensures all testing is performed only on authorized systems.
    
    Example:
        >>> manager = TargetManager(config)
        >>> manager.authorize_target(
        ...     identifier="192.168.1.100",
        ...     authorization_token="AUTH-2024-001",
        ...     authorized_by="security@example.com"
        ... )
        >>> manager.is_authorized("192.168.1.100")
        True
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Target Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Authorized targets
        self.targets: Dict[str, Target] = {}
        
        # Allowed/forbidden target lists from config
        self.allowed_networks = self._parse_networks(
            self.config.get("allowed_targets", [])
        )
        self.forbidden_networks = self._parse_networks(
            self.config.get("forbidden_targets", [])
        )
        
        logger.info(f"TargetManager initialized")
        logger.info(f"Allowed networks: {len(self.allowed_networks)}")
        logger.info(f"Forbidden networks: {len(self.forbidden_networks)}")
    
    def _parse_networks(self, networks: List[str]) -> List[ipaddress.IPv4Network]:
        """Parse network CIDRs."""
        parsed = []
        for net in networks:
            try:
                parsed.append(ipaddress.ip_network(net, strict=False))
            except ValueError:
                logger.warning(f"Invalid network CIDR: {net}")
        return parsed
    
    def authorize_target(
        self,
        identifier: str,
        authorization_token: str,
        authorized_by: str,
        description: Optional[str] = None,
        scope: Optional[List[str]] = None,
        expires_at: Optional[str] = None
    ) -> Target:
        """
        Authorize a target for security testing.
        
        Args:
            identifier: Target IP, hostname, or CIDR
            authorization_token: Authorization proof
            authorized_by: Authorizing party
            description: Target description
            scope: Services/ports in scope
            expires_at: Authorization expiration
            
        Returns:
            Target object
        """
        target_id = f"target_{len(self.targets)}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        target = Target(
            target_id=target_id,
            identifier=identifier,
            description=description or f"Target {identifier}",
            authorization_token=authorization_token,
            authorized_by=authorized_by,
            authorized_at=datetime.now().isoformat(),
            expires_at=expires_at,
            scope=scope or ["*"],  # Default to all in scope
            out_of_scope=[],
            metadata={}
        )
        
        self.targets[identifier] = target
        
        logger.info(f"Target authorized: {identifier} by {authorized_by}")
        return target
    
    def revoke_target(self, identifier: str) -> bool:
        """
        Revoke target authorization.
        
        Args:
            identifier: Target identifier
            
        Returns:
            True if revoked
        """
        if identifier in self.targets:
            del self.targets[identifier]
            logger.info(f"Target authorization revoked: {identifier}")
            return True
        
        logger.warning(f"Target not found: {identifier}")
        return False
    
    def is_authorized(self, identifier: str) -> bool:
        """
        Check if target is authorized.
        
        Args:
            identifier: Target IP, hostname, or CIDR
            
        Returns:
            True if authorized
        """
        # Check explicit authorization
        if identifier in self.targets:
            target = self.targets[identifier]
            
            # Check expiration
            if target.expires_at:
                try:
                    expires = datetime.fromisoformat(target.expires_at)
                    if datetime.now() > expires:
                        logger.warning(f"Target authorization expired: {identifier}")
                        return False
                except ValueError:
                    pass
            
            return True
        
        # Check if in allowed networks
        if self._is_in_networks(identifier, self.allowed_networks):
            # But not in forbidden networks
            if not self._is_in_networks(identifier, self.forbidden_networks):
                return True
        
        return False
    
    def _is_in_networks(
        self,
        identifier: str,
        networks: List[ipaddress.IPv4Network]
    ) -> bool:
        """Check if identifier is in any of the networks."""
        try:
            ip = ipaddress.ip_address(identifier)
            return any(ip in network for network in networks)
        except ValueError:
            # Not a valid IP, could be hostname
            return False
    
    def get_target(self, identifier: str) -> Optional[Target]:
        """
        Get target by identifier.
        
        Args:
            identifier: Target identifier
            
        Returns:
            Target object or None
        """
        return self.targets.get(identifier)
    
    def list_targets(
        self,
        active_only: bool = True
    ) -> List[Target]:
        """
        List authorized targets.
        
        Args:
            active_only: Only return non-expired targets
            
        Returns:
            List of targets
        """
        targets = list(self.targets.values())
        
        if active_only:
            now = datetime.now()
            targets = [
                t for t in targets
                if not t.expires_at or datetime.fromisoformat(t.expires_at) > now
            ]
        
        return targets
    
    def is_in_scope(
        self,
        identifier: str,
        service: str
    ) -> bool:
        """
        Check if service is in scope for target.
        
        Args:
            identifier: Target identifier
            service: Service or port to check
            
        Returns:
            True if in scope
        """
        target = self.get_target(identifier)
        if not target:
            return False
        
        # Check out of scope
        if service in target.out_of_scope:
            return False
        
        # Check in scope
        if "*" in target.scope:
            return True
        
        return service in target.scope
    
    def add_to_scope(
        self,
        identifier: str,
        services: List[str]
    ) -> bool:
        """
        Add services to target scope.
        
        Args:
            identifier: Target identifier
            services: Services to add
            
        Returns:
            True if updated
        """
        target = self.get_target(identifier)
        if not target:
            return False
        
        target.scope.extend(services)
        logger.info(f"Added to scope for {identifier}: {services}")
        return True
    
    def remove_from_scope(
        self,
        identifier: str,
        services: List[str]
    ) -> bool:
        """
        Remove services from scope (add to out-of-scope).
        
        Args:
            identifier: Target identifier
            services: Services to exclude
            
        Returns:
            True if updated
        """
        target = self.get_target(identifier)
        if not target:
            return False
        
        target.out_of_scope.extend(services)
        logger.info(f"Removed from scope for {identifier}: {services}")
        return True
    
    def validate_target(self, identifier: str) -> Dict[str, Any]:
        """
        Validate target identifier format and authorization.
        
        Args:
            identifier: Target to validate
            
        Returns:
            Validation results
        """
        results = {
            "identifier": identifier,
            "valid_format": False,
            "authorized": False,
            "in_allowed_networks": False,
            "in_forbidden_networks": False,
            "type": "unknown"
        }
        
        # Check format
        # IP address
        try:
            ip = ipaddress.ip_address(identifier)
            results["valid_format"] = True
            results["type"] = "ip"
        except ValueError:
            pass
        
        # CIDR network
        if not results["valid_format"]:
            try:
                net = ipaddress.ip_network(identifier, strict=False)
                results["valid_format"] = True
                results["type"] = "network"
            except ValueError:
                pass
        
        # Hostname
        if not results["valid_format"]:
            # Simple hostname validation
            hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
            if re.match(hostname_pattern, identifier):
                results["valid_format"] = True
                results["type"] = "hostname"
        
        # Check authorization
        results["authorized"] = self.is_authorized(identifier)
        results["in_allowed_networks"] = self._is_in_networks(identifier, self.allowed_networks)
        results["in_forbidden_networks"] = self._is_in_networks(identifier, self.forbidden_networks)
        
        return results


__all__ = ["TargetManager", "Target"]
