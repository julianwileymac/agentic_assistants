"""
Network management for security operations.
"""

from .vpn_manager import VPNManager, VPNProfile, VPNStatus
from .target_manager import TargetManager, Target
from .international_resources import InternationalResources, TestResource, LegalFramework

__all__ = [
    "VPNManager",
    "VPNProfile",
    "VPNStatus",
    "TargetManager",
    "Target",
    "InternationalResources",
    "TestResource",
    "LegalFramework",
]
