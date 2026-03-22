"""
International Security Testing Resources.

Provides access to legal security testing resources across countries.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestResource:
    """Security testing resource."""
    resource_id: str
    name: str
    url: str
    country: str
    resource_type: str  # platform, target, range
    description: str
    legal_status: str  # legal, requires_permission, restricted
    access_method: str  # vpn, direct, proxy
    credentials_required: bool
    cost: str  # free, paid, subscription
    tags: List[str]


@dataclass
class LegalFramework:
    """Legal framework for security testing."""
    country: str
    computer_misuse_law: str
    authorization_required: bool
    penalties: str
    safe_harbor: bool
    notes: str
    references: List[str]


class InternationalResources:
    """
    Manages international security testing resources.
    
    Provides curated list of legal testing resources and
    legal frameworks for different countries.
    
    Example:
        >>> resources = InternationalResources()
        >>> platforms = resources.get_resources(country="US", resource_type="platform")
        >>> legal = resources.get_legal_framework("US")
    """
    
    def __init__(self):
        """Initialize international resources."""
        self.resources = self._load_resources()
        self.legal_frameworks = self._load_legal_frameworks()
        
        logger.info(f"Loaded {len(self.resources)} international resources")
        logger.info(f"Loaded {len(self.legal_frameworks)} legal frameworks")
    
    def _load_resources(self) -> List[TestResource]:
        """Load security testing resources."""
        resources = []
        
        # Intentionally Vulnerable Platforms
        resources.append(TestResource(
            resource_id="hackthebox",
            name="HackTheBox",
            url="https://www.hackthebox.com",
            country="International",
            resource_type="platform",
            description="Penetration testing labs and challenges",
            legal_status="legal",
            access_method="direct",
            credentials_required=True,
            cost="freemium",
            tags=["ctf", "labs", "challenges"]
        ))
        
        resources.append(TestResource(
            resource_id="tryhackme",
            name="TryHackMe",
            url="https://tryhackme.com",
            country="International",
            resource_type="platform",
            description="Guided cybersecurity training",
            legal_status="legal",
            access_method="direct",
            credentials_required=True,
            cost="freemium",
            tags=["training", "labs", "guided"]
        ))
        
        resources.append(TestResource(
            resource_id="pentesterlab",
            name="PentesterLab",
            url="https://pentesterlab.com",
            country="International",
            resource_type="platform",
            description="Web penetration testing exercises",
            legal_status="legal",
            access_method="direct",
            credentials_required=True,
            cost="subscription",
            tags=["web", "training"]
        ))
        
        resources.append(TestResource(
            resource_id="vulnhub",
            name="VulnHub",
            url="https://www.vulnhub.com",
            country="International",
            resource_type="target",
            description="Vulnerable VMs for practice",
            legal_status="legal",
            access_method="download",
            credentials_required=False,
            cost="free",
            tags=["vms", "offline"]
        ))
        
        # Test Target Websites
        resources.append(TestResource(
            resource_id="dvwa",
            name="Damn Vulnerable Web Application",
            url="https://github.com/digininja/DVWA",
            country="International",
            resource_type="target",
            description="Intentionally vulnerable PHP/MySQL web app",
            legal_status="legal",
            access_method="local",
            credentials_required=False,
            cost="free",
            tags=["web", "local", "php"]
        ))
        
        resources.append(TestResource(
            resource_id="webgoat",
            name="OWASP WebGoat",
            url="https://owasp.org/www-project-webgoat/",
            country="International",
            resource_type="target",
            description="Deliberately insecure web application",
            legal_status="legal",
            access_method="local",
            credentials_required=False,
            cost="free",
            tags=["web", "local", "owasp"]
        ))
        
        resources.append(TestResource(
            resource_id="bwapp",
            name="bWAPP",
            url="http://www.itsecgames.com/",
            country="International",
            resource_type="target",
            description="Buggy web application",
            legal_status="legal",
            access_method="local",
            credentials_required=False,
            cost="free",
            tags=["web", "local"]
        ))
        
        # Country-Specific Bug Bounty Platforms
        resources.append(TestResource(
            resource_id="hackerone",
            name="HackerOne",
            url="https://www.hackerone.com",
            country="International",
            resource_type="platform",
            description="Bug bounty and vulnerability disclosure",
            legal_status="legal",
            access_method="direct",
            credentials_required=True,
            cost="free",
            tags=["bug-bounty", "responsible-disclosure"]
        ))
        
        resources.append(TestResource(
            resource_id="bugcrowd",
            name="Bugcrowd",
            url="https://www.bugcrowd.com",
            country="International",
            resource_type="platform",
            description="Crowdsourced cybersecurity",
            legal_status="legal",
            access_method="direct",
            credentials_required=True,
            cost="free",
            tags=["bug-bounty"]
        ))
        
        return resources
    
    def _load_legal_frameworks(self) -> Dict[str, LegalFramework]:
        """Load legal frameworks by country."""
        frameworks = {}
        
        # United States
        frameworks["US"] = LegalFramework(
            country="United States",
            computer_misuse_law="Computer Fraud and Abuse Act (CFAA)",
            authorization_required=True,
            penalties="Up to 20 years imprisonment and fines",
            safe_harbor=True,
            notes="Requires explicit authorization. Safe harbor under DMCA 1201 for security research.",
            references=[
                "18 U.S.C. § 1030",
                "https://www.law.cornell.edu/uscode/text/18/1030"
            ]
        )
        
        # United Kingdom
        frameworks["UK"] = LegalFramework(
            country="United Kingdom",
            computer_misuse_law="Computer Misuse Act 1990",
            authorization_required=True,
            penalties="Up to 10 years imprisonment",
            safe_harbor=False,
            notes="Unauthorized access is criminal. No explicit safe harbor for researchers.",
            references=[
                "Computer Misuse Act 1990",
                "https://www.legislation.gov.uk/ukpga/1990/18/contents"
            ]
        )
        
        # European Union
        frameworks["EU"] = LegalFramework(
            country="European Union",
            computer_misuse_law="Directive 2013/40/EU",
            authorization_required=True,
            penalties="Varies by member state",
            safe_harbor=False,
            notes="EU directive on attacks against information systems. Member states implement locally.",
            references=[
                "Directive 2013/40/EU",
                "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013L0040"
            ]
        )
        
        # Australia
        frameworks["AU"] = LegalFramework(
            country="Australia",
            computer_misuse_law="Criminal Code Act 1995",
            authorization_required=True,
            penalties="Up to 10 years imprisonment",
            safe_harbor=False,
            notes="Unauthorized access and modification are criminal offenses.",
            references=[
                "Criminal Code Act 1995 - Part 10.7",
                "https://www.legislation.gov.au/Details/C2021C00449"
            ]
        )
        
        return frameworks
    
    def get_resources(
        self,
        country: Optional[str] = None,
        resource_type: Optional[str] = None,
        cost: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[TestResource]:
        """
        Get security testing resources.
        
        Args:
            country: Filter by country
            resource_type: Filter by type
            cost: Filter by cost (free, paid, freemium)
            tags: Filter by tags
            
        Returns:
            List of matching resources
        """
        results = self.resources
        
        if country:
            results = [r for r in results if r.country.lower() == country.lower() or r.country.lower() == "international"]
        
        if resource_type:
            results = [r for r in results if r.resource_type == resource_type]
        
        if cost:
            results = [r for r in results if r.cost == cost]
        
        if tags:
            results = [r for r in results if any(tag in r.tags for tag in tags)]
        
        return results
    
    def get_legal_framework(self, country: str) -> Optional[LegalFramework]:
        """
        Get legal framework for country.
        
        Args:
            country: Country code (e.g., "US", "UK")
            
        Returns:
            LegalFramework or None
        """
        return self.legal_frameworks.get(country.upper())
    
    def check_legality(
        self,
        country: str,
        has_authorization: bool
    ) -> Dict[str, Any]:
        """
        Check legality of security testing in country.
        
        Args:
            country: Country code
            has_authorization: Whether explicit authorization exists
            
        Returns:
            Legality assessment
        """
        framework = self.get_legal_framework(country)
        
        if not framework:
            return {
                "country": country,
                "status": "unknown",
                "message": "Legal framework not available for this country",
                "recommendation": "Consult local legal counsel"
            }
        
        if not has_authorization:
            return {
                "country": country,
                "status": "illegal",
                "message": "Authorization required by law",
                "law": framework.computer_misuse_law,
                "penalties": framework.penalties,
                "recommendation": "Obtain explicit written authorization"
            }
        
        return {
            "country": country,
            "status": "legal",
            "message": "Testing permitted with authorization",
            "law": framework.computer_misuse_law,
            "safe_harbor": framework.safe_harbor,
            "recommendation": "Maintain authorization documentation"
        }
    
    def get_recommendations(self, country: str) -> List[str]:
        """
        Get security testing recommendations for country.
        
        Args:
            country: Country code
            
        Returns:
            List of recommendations
        """
        recommendations = [
            "Always obtain explicit written authorization",
            "Document all testing activities",
            "Stay within authorized scope",
            "Report findings responsibly",
            "Respect data privacy laws"
        ]
        
        framework = self.get_legal_framework(country)
        if framework:
            if not framework.safe_harbor:
                recommendations.append("No safe harbor provisions - extra caution required")
            
            if framework.authorization_required:
                recommendations.append("Legal authorization is mandatory")
        
        return recommendations


__all__ = ["InternationalResources", "TestResource", "LegalFramework"]
