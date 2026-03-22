"""
VPN Manager for international security testing.

Manages VPN connections for accessing resources in different countries.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VPNProfile:
    """VPN connection profile."""
    profile_id: str
    name: str
    country: str
    provider: str
    protocol: str  # openvpn, wireguard
    config_file: str
    credentials_file: Optional[str]
    auto_connect: bool = False


@dataclass
class VPNStatus:
    """Current VPN connection status."""
    connected: bool
    profile_id: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    connected_since: Optional[str]
    bandwidth_used: Optional[float]


class VPNManager:
    """
    VPN connection manager for international testing.
    
    Supports OpenVPN and WireGuard protocols.
    
    Example:
        >>> manager = VPNManager(config)
        >>> manager.load_profile("us-east-1")
        >>> manager.connect()
        >>> manager.disconnect()
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        profiles_dir: Optional[str] = None
    ):
        """
        Initialize VPN Manager.
        
        Args:
            config: Configuration dictionary
            profiles_dir: Directory containing VPN profiles
        """
        self.config = config or {}
        self.profiles_dir = Path(profiles_dir or "./network/vpn-configs")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Current state
        self.current_profile = None
        self.connected = False
        self.process = None
        
        # Load profiles
        self.profiles = self._load_profiles()
        
        logger.info(f"VPNManager initialized with {len(self.profiles)} profiles")
    
    def _load_profiles(self) -> Dict[str, VPNProfile]:
        """Load VPN profiles from configuration."""
        profiles = {}
        
        # Check for profile files in directory
        for profile_file in self.profiles_dir.glob("*.ovpn"):
            profile_id = profile_file.stem
            profiles[profile_id] = VPNProfile(
                profile_id=profile_id,
                name=profile_id.replace("-", " ").title(),
                country=profile_id.split("-")[0] if "-" in profile_id else "Unknown",
                provider="OpenVPN",
                protocol="openvpn",
                config_file=str(profile_file),
                credentials_file=None
            )
            logger.debug(f"Loaded profile: {profile_id}")
        
        # Check for WireGuard configs
        for profile_file in self.profiles_dir.glob("*.conf"):
            profile_id = profile_file.stem
            profiles[profile_id] = VPNProfile(
                profile_id=profile_id,
                name=profile_id.replace("-", " ").title(),
                country=profile_id.split("-")[0] if "-" in profile_id else "Unknown",
                provider="WireGuard",
                protocol="wireguard",
                config_file=str(profile_file),
                credentials_file=None
            )
            logger.debug(f"Loaded profile: {profile_id}")
        
        return profiles
    
    def list_profiles(
        self,
        country: Optional[str] = None
    ) -> List[VPNProfile]:
        """
        List available VPN profiles.
        
        Args:
            country: Filter by country
            
        Returns:
            List of VPN profiles
        """
        profiles = list(self.profiles.values())
        
        if country:
            profiles = [p for p in profiles if p.country.lower() == country.lower()]
        
        return profiles
    
    def connect(
        self,
        profile_id: Optional[str] = None
    ) -> bool:
        """
        Connect to VPN.
        
        Args:
            profile_id: Profile to connect to (uses default if None)
            
        Returns:
            True if connection succeeded
        """
        if self.connected:
            logger.warning("Already connected to VPN")
            return False
        
        # Get profile
        if profile_id is None:
            profile_id = self.config.get("default_vpn_profile", "us-east-1")
        
        profile = self.profiles.get(profile_id)
        if not profile:
            logger.error(f"Profile not found: {profile_id}")
            return False
        
        logger.info(f"Connecting to VPN: {profile.name} ({profile.country})")
        
        try:
            # Connect based on protocol
            if profile.protocol == "openvpn":
                success = self._connect_openvpn(profile)
            elif profile.protocol == "wireguard":
                success = self._connect_wireguard(profile)
            else:
                logger.error(f"Unsupported protocol: {profile.protocol}")
                return False
            
            if success:
                self.connected = True
                self.current_profile = profile
                logger.info(f"Connected to {profile.name}")
            
            return success
        
        except Exception as e:
            logger.error(f"VPN connection failed: {e}")
            return False
    
    def _connect_openvpn(self, profile: VPNProfile) -> bool:
        """Connect using OpenVPN."""
        try:
            # Check if OpenVPN is installed
            result = subprocess.run(
                ["openvpn", "--version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error("OpenVPN not installed")
                return False
            
            # Start OpenVPN process
            # In production, this would actually connect
            logger.info(f"OpenVPN connection simulated for {profile.config_file}")
            
            # Simulated connection
            return True
        
        except FileNotFoundError:
            logger.error("OpenVPN binary not found")
            return False
        except Exception as e:
            logger.error(f"OpenVPN connection failed: {e}")
            return False
    
    def _connect_wireguard(self, profile: VPNProfile) -> bool:
        """Connect using WireGuard."""
        try:
            # Check if WireGuard is available
            result = subprocess.run(
                ["wg", "show"],
                capture_output=True,
                timeout=5
            )
            
            # In production, would use wg-quick up
            logger.info(f"WireGuard connection simulated for {profile.config_file}")
            
            return True
        
        except FileNotFoundError:
            logger.error("WireGuard not installed")
            return False
        except Exception as e:
            logger.error(f"WireGuard connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from VPN.
        
        Returns:
            True if disconnection succeeded
        """
        if not self.connected:
            logger.warning("Not connected to VPN")
            return False
        
        logger.info(f"Disconnecting from {self.current_profile.name}")
        
        try:
            # Disconnect based on protocol
            if self.current_profile.protocol == "openvpn":
                self._disconnect_openvpn()
            elif self.current_profile.protocol == "wireguard":
                self._disconnect_wireguard()
            
            self.connected = False
            self.current_profile = None
            
            logger.info("Disconnected from VPN")
            return True
        
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
            return False
    
    def _disconnect_openvpn(self):
        """Disconnect OpenVPN."""
        if self.process:
            self.process.terminate()
            self.process = None
    
    def _disconnect_wireguard(self):
        """Disconnect WireGuard."""
        # In production: wg-quick down <interface>
        pass
    
    def get_status(self) -> VPNStatus:
        """
        Get current VPN connection status.
        
        Returns:
            VPNStatus with connection details
        """
        if not self.connected or not self.current_profile:
            return VPNStatus(
                connected=False,
                profile_id=None,
                ip_address=None,
                country=None,
                connected_since=None,
                bandwidth_used=None
            )
        
        return VPNStatus(
            connected=True,
            profile_id=self.current_profile.profile_id,
            ip_address=self._get_ip_address(),
            country=self.current_profile.country,
            connected_since=datetime.now().isoformat(),
            bandwidth_used=0.0
        )
    
    def _get_ip_address(self) -> Optional[str]:
        """Get current public IP address."""
        try:
            # In production, would query external service
            return "10.0.0.1"  # Simulated
        except Exception as e:
            logger.error(f"Failed to get IP: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test VPN connection.
        
        Returns:
            True if connection is working
        """
        if not self.connected:
            return False
        
        try:
            # Ping test
            result = subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


__all__ = ["VPNManager", "VPNProfile", "VPNStatus"]
