"""
Security Assistant with RAG (Retrieval-Augmented Generation).

Provides AI-powered security guidance and recommendations.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AssistantResponse:
    """Response from security assistant."""
    query: str
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    timestamp: str
    metadata: Dict[str, Any]


class SecurityAssistant:
    """
    AI-powered security assistant with RAG.
    
    Provides:
    - Security best practices guidance
    - Tool usage recommendations
    - Vulnerability remediation advice
    - Attack technique explanations
    - Interactive Q&A
    
    Example:
        >>> assistant = SecurityAssistant(config, knowledge_base, tool_manager)
        >>> response = assistant.chat("How do I secure SSH?")
        >>> recommendation = assistant.recommend_tool("web vulnerability scanning")
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        knowledge_base,
        tool_manager
    ):
        """
        Initialize Security Assistant.
        
        Args:
            config: Assistant configuration
            knowledge_base: Vector knowledge base for RAG
            tool_manager: Tool manager for tool recommendations
        """
        self.config = config
        self.knowledge_base = knowledge_base
        self.tool_manager = tool_manager
        
        # Assistant settings
        self.model = config.get("model", "llama3:8b")
        self.temperature = config.get("temperature", 0.3)
        self.max_context = config.get("max_context", 4096)
        self.num_retrieved = config.get("num_retrieved", 5)
        
        # Conversation history
        self.conversation_history = []
        
        logger.info(f"SecurityAssistant initialized with model: {self.model}")
    
    def chat(
        self,
        query: str,
        include_sources: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> AssistantResponse:
        """
        Chat with the security assistant.
        
        Args:
            query: User query
            include_sources: Include source references
            context: Additional context
            
        Returns:
            AssistantResponse with answer and sources
        """
        logger.info(f"Assistant query: {query}")
        
        # Retrieve relevant context from knowledge base
        retrieved_docs = self._retrieve_context(query)
        
        # Build prompt with context
        prompt = self._build_prompt(query, retrieved_docs, context)
        
        # Generate response (simplified - would use actual LLM)
        response_text = self._generate_response(prompt, query, retrieved_docs)
        
        # Track conversation
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response_text
        })
        
        return AssistantResponse(
            query=query,
            response=response_text,
            sources=retrieved_docs if include_sources else [],
            confidence=0.85,  # Would come from model
            timestamp=datetime.now().isoformat(),
            metadata={"model": self.model}
        )
    
    def _retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant context from knowledge base."""
        if not self.knowledge_base:
            return []
        
        try:
            # Search multiple collections
            collections = [
                "cybersec-tools",
                "cybersec-exploits",
                "cybersec-vulnerabilities"
            ]
            
            all_results = []
            for collection in collections:
                try:
                    results = self.knowledge_base.search(
                        collection=collection,
                        query=query,
                        limit=self.num_retrieved // len(collections)
                    )
                    all_results.extend(results)
                except Exception as e:
                    logger.debug(f"Search failed for {collection}: {e}")
            
            return all_results[:self.num_retrieved]
        
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    def _build_prompt(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt with retrieved context."""
        prompt = """You are an expert cybersecurity assistant. Answer the user's question using the provided context.

Context from knowledge base:
"""
        
        for i, doc in enumerate(context_docs, 1):
            prompt += f"\n{i}. {doc.get('text', '')[:500]}\n"
        
        if additional_context:
            prompt += f"\nAdditional context: {additional_context}\n"
        
        prompt += f"\nUser question: {query}\n\nAnswer:"
        
        return prompt
    
    def _generate_response(
        self,
        prompt: str,
        query: str,
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate response using LLM.
        
        In production, this would use Ollama or similar.
        For now, provides rule-based responses.
        """
        query_lower = query.lower()
        
        # Rule-based responses for common queries
        if "ssh" in query_lower and ("secure" in query_lower or "harden" in query_lower):
            return """To secure SSH:

1. **Disable root login**: Set `PermitRootLogin no` in /etc/ssh/sshd_config
2. **Use key-based authentication**: Disable password authentication
3. **Change default port**: Use a non-standard port (e.g., 2222)
4. **Enable firewall**: Use UFW or iptables to restrict access
5. **Use strong ciphers**: Configure modern encryption algorithms
6. **Enable 2FA**: Use Google Authenticator or similar
7. **Limit user access**: Use AllowUsers or AllowGroups
8. **Monitor logs**: Check /var/log/auth.log regularly
9. **Update regularly**: Keep SSH version current
10. **Use fail2ban**: Automatically block brute force attempts

Example configuration:
```
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers alice bob
```

Remember to restart SSH after changes: `sudo systemctl restart sshd`"""
        
        elif "nmap" in query_lower:
            return """Nmap is a powerful network scanning tool. Common usage:

**Basic scans:**
- `nmap <target>` - Basic port scan
- `nmap -sV <target>` - Service version detection
- `nmap -O <target>` - OS detection
- `nmap -A <target>` - Aggressive scan (OS, version, scripts)

**Stealth scans:**
- `nmap -sS <target>` - SYN scan (stealthy)
- `nmap -sN <target>` - NULL scan
- `nmap -T2 <target>` - Slow timing (less detectable)

**Port specification:**
- `nmap -p 22,80,443 <target>` - Specific ports
- `nmap -p- <target>` - All ports (1-65535)
- `nmap -p 1-1000 <target>` - Port range

**Vulnerability scanning:**
- `nmap --script vuln <target>` - Run vulnerability scripts
- `nmap --script http-vuln-* <target>` - HTTP vulnerabilities

Always ensure you have permission to scan targets!"""
        
        elif "sql injection" in query_lower or "sqlmap" in query_lower:
            return """SQL Injection testing with SQLMap:

**Basic usage:**
```bash
sqlmap -u "http://target.com/page?id=1" --batch
```

**Common options:**
- `--dbs` - Enumerate databases
- `--tables` - List tables
- `--dump` - Dump table contents
- `--os-shell` - Get OS shell (if possible)

**POST request:**
```bash
sqlmap -u "http://target.com/login" --data="user=admin&pass=test"
```

**With cookies:**
```bash
sqlmap -u "http://target.com/page?id=1" --cookie="session=abc123"
```

**Best practices:**
1. Always get written authorization
2. Start with safe options (--batch, --skip-waf)
3. Document all findings
4. Don't damage the target system
5. Report responsibly

**Prevention:**
- Use prepared statements
- Validate all input
- Apply principle of least privilege
- Keep frameworks updated
- Use WAF (Web Application Firewall)"""
        
        elif "vulnerability" in query_lower and ("prioritize" in query_lower or "remediate" in query_lower):
            return """Vulnerability Prioritization:

**Priority Framework (CVSS + Context):**

1. **Critical (Score 9.0-10.0):**
   - Remediate immediately (0-24 hours)
   - Active exploits in the wild
   - Affects critical systems
   - Example: Unauthenticated RCE

2. **High (Score 7.0-8.9):**
   - Remediate within 24-48 hours
   - Exploits available but not widespread
   - Example: Authenticated RCE, privilege escalation

3. **Medium (Score 4.0-6.9):**
   - Remediate within 1-2 weeks
   - Lower exploitability
   - Example: XSS, CSRF, information disclosure

4. **Low (Score 0.1-3.9):**
   - Address during regular maintenance
   - Minimal impact
   - Example: Version disclosure, minor config issues

**Factors to Consider:**
- Asset criticality (public-facing, contains PII?)
- Exploitability (exploit code available?)
- Business impact (revenue, reputation)
- Compliance requirements (PCI-DSS, HIPAA)
- Attack surface exposure

**Remediation Steps:**
1. Verify vulnerability exists
2. Test patches in staging
3. Apply patches to production
4. Verify fix effectiveness
5. Document the process
6. Update security policies"""
        
        elif context_docs:
            # If we have context but no specific rule, provide a generic response
            return f"""Based on the security information available:

{context_docs[0].get('text', '')[:500] if context_docs else 'No specific information found.'}

For more detailed guidance on "{query}", I recommend:
1. Reviewing the official documentation
2. Consulting OWASP resources
3. Testing in a safe environment
4. Seeking expert advice if needed

Would you like more specific information about any aspect?"""
        
        else:
            return f"""I can help with cybersecurity topics including:

- Tool usage and recommendations (nmap, sqlmap, metasploit, etc.)
- Vulnerability assessment and remediation
- Security best practices
- Attack techniques and defenses
- Configuration hardening
- Incident response

Could you please provide more details about what you'd like to know regarding "{query}"?"""
    
    def recommend_tool(
        self,
        task: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend security tool(s) for a task.
        
        Args:
            task: Security task description
            constraints: Constraints (os, category, etc.)
            
        Returns:
            Tool recommendations
        """
        logger.info(f"Recommending tools for: {task}")
        
        task_lower = task.lower()
        recommendations = []
        
        # Get available tools
        tools = self.tool_manager.list_tools()
        
        # Match task to tools
        if "network" in task_lower or "port scan" in task_lower:
            matching = [t for t in tools if t.category == "network"]
            recommendations.extend(matching[:3])
        
        elif "web" in task_lower or "website" in task_lower:
            matching = [t for t in tools if t.category == "web"]
            recommendations.extend(matching[:3])
        
        elif "password" in task_lower or "crack" in task_lower:
            matching = [t for t in tools if t.category == "password"]
            recommendations.extend(matching[:3])
        
        elif "exploit" in task_lower:
            matching = [t for t in tools if t.category == "exploit"]
            recommendations.extend(matching[:2])
        
        else:
            # General recommendations
            recommendations = tools[:5]
        
        # Apply constraints
        if constraints:
            os_filter = constraints.get("os")
            if os_filter:
                recommendations = [
                    t for t in recommendations
                    if os_filter in t.os_support
                ]
        
        return {
            "task": task,
            "recommendations": [
                {
                    "name": t.name,
                    "category": t.category,
                    "description": t.description,
                    "status": t.status.value,
                    "capabilities": t.capabilities
                }
                for t in recommendations
            ],
            "advice": self._get_tool_advice(task, recommendations)
        }
    
    def _get_tool_advice(self, task: str, tools: List[Any]) -> str:
        """Get advice for using recommended tools."""
        if not tools:
            return "No specific tools found. Consider using general-purpose tools like nmap or Burp Suite."
        
        tool_names = [t.name for t in tools[:3]]
        
        return f"""For {task}, I recommend starting with: {', '.join(tool_names)}.

General advice:
1. Always get proper authorization before testing
2. Start with non-intrusive scans
3. Document all findings
4. Follow responsible disclosure practices
5. Keep tools updated for best results

Would you like specific guidance on using any of these tools?"""
    
    def explain_technique(
        self,
        technique_id: str
    ) -> Dict[str, Any]:
        """
        Explain a MITRE ATT&CK technique.
        
        Args:
            technique_id: MITRE ATT&CK technique ID (e.g., T1190)
            
        Returns:
            Technique explanation
        """
        # This would query MITRE ATT&CK database
        # For now, provide generic structure
        
        return {
            "technique_id": technique_id,
            "name": "Technique Name",
            "tactic": "Initial Access",
            "description": "Technique description from MITRE ATT&CK",
            "detection": "Detection methods",
            "mitigation": "Mitigation strategies",
            "examples": ["Real-world examples"],
            "references": ["https://attack.mitre.org/"]
        }
    
    def get_conversation_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history."""
        history = self.conversation_history
        if limit:
            history = history[-limit:]
        return history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")


__all__ = ["SecurityAssistant", "AssistantResponse"]
