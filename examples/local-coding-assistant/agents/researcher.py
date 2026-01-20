"""
Research Agent for deep code analysis.

Performs thorough investigation of codebases and provides
comprehensive reports on architecture, patterns, and issues.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ResearchReport:
    """Research report from the agent."""
    
    topic: str
    summary: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchAgent:
    """
    Research agent for deep code analysis.
    
    Performs thorough investigation of codebases, analyzes
    architecture decisions, and provides comprehensive reports.
    
    Example:
        >>> agent = ResearchAgent()
        >>> report = agent.investigate("How does the caching layer work?")
        >>> print(report.summary)
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are a thorough technical researcher. Your job is to deeply analyze
codebases, understand architecture decisions, and provide comprehensive reports.

Focus on:
- Understanding the overall architecture
- Identifying patterns and anti-patterns
- Finding potential issues and improvements
- Documenting findings clearly

When researching:
1. Start with a high-level overview
2. Dive into specific components
3. Analyze relationships and dependencies
4. Identify strengths and weaknesses
5. Provide actionable recommendations"""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        vectordb_collection: str = "codebase",
    ):
        """
        Initialize the research agent.
        
        Args:
            system_prompt: Custom system prompt
            llm_config: LLM configuration
            vectordb_collection: Vector store collection
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm_config = llm_config or {}
        self.vectordb_collection = vectordb_collection
        self._vectordb = None
    
    @property
    def vectordb(self):
        """Get vector store."""
        if self._vectordb is None:
            from agentic_assistants.vectordb.scoped_store import ScopedVectorStore
            self._vectordb = ScopedVectorStore()
        return self._vectordb
    
    def investigate(
        self,
        topic: str,
        depth: str = "medium",
        max_sources: int = 10,
    ) -> ResearchReport:
        """
        Investigate a topic in the codebase.
        
        Args:
            topic: Topic to research
            depth: Research depth (shallow, medium, deep)
            max_sources: Maximum sources to analyze
            
        Returns:
            ResearchReport with findings
        """
        # Search for relevant code
        results = self.vectordb.search(
            query=topic,
            collection=self.vectordb_collection,
            top_k=max_sources,
        )
        
        # Build context from sources
        sources = []
        context_parts = []
        
        for r in results:
            source_info = {
                "file": r.document.metadata.get("source", "unknown"),
                "score": r.score,
            }
            sources.append(source_info)
            context_parts.append(
                f"File: {source_info['file']}\n```\n{r.document.content}\n```"
            )
        
        context = "\n\n".join(context_parts)
        
        # Generate analysis
        depth_instructions = {
            "shallow": "Provide a brief overview focusing on key points.",
            "medium": "Provide a comprehensive analysis with examples.",
            "deep": "Perform an exhaustive analysis covering all aspects.",
        }
        
        prompt = f"""Research topic: {topic}

{depth_instructions.get(depth, depth_instructions['medium'])}

Based on the following code samples, provide:
1. A summary of how this works
2. Key findings (list each with evidence from the code)
3. Recommendations for improvement

Code samples:
{context}"""
        
        response = self._call_llm(prompt)
        
        # Parse response into structured report
        return ResearchReport(
            topic=topic,
            summary=self._extract_summary(response),
            findings=self._extract_findings(response),
            recommendations=self._extract_recommendations(response),
            sources=sources,
            metadata={"depth": depth, "sources_analyzed": len(sources)},
        )
    
    def analyze_architecture(
        self,
        focus_areas: Optional[List[str]] = None,
    ) -> ResearchReport:
        """
        Analyze the overall architecture.
        
        Args:
            focus_areas: Specific areas to focus on
            
        Returns:
            ResearchReport on architecture
        """
        focus = focus_areas or ["structure", "patterns", "dependencies"]
        
        # Search for architecture-related code
        queries = [
            "main entry point initialization",
            "configuration settings",
            "dependency injection",
            "service layer",
        ]
        
        all_results = []
        for query in queries:
            results = self.vectordb.search(
                query=query,
                collection=self.vectordb_collection,
                top_k=3,
            )
            all_results.extend(results)
        
        context_parts = []
        sources = []
        
        for r in all_results[:15]:  # Limit total
            source_info = {
                "file": r.document.metadata.get("source", "unknown"),
                "score": r.score,
            }
            if source_info not in sources:
                sources.append(source_info)
                context_parts.append(
                    f"File: {source_info['file']}\n```\n{r.document.content[:500]}\n```"
                )
        
        context = "\n\n".join(context_parts)
        focus_str = ", ".join(focus)
        
        prompt = f"""Analyze the architecture of this codebase focusing on: {focus_str}

Provide:
1. Overall architecture description
2. Key architectural patterns identified
3. Component relationships
4. Strengths of the current architecture
5. Potential architectural improvements

Code samples:
{context}"""
        
        response = self._call_llm(prompt)
        
        return ResearchReport(
            topic="Architecture Analysis",
            summary=self._extract_summary(response),
            findings=self._extract_findings(response),
            recommendations=self._extract_recommendations(response),
            sources=sources,
            metadata={"focus_areas": focus},
        )
    
    def find_patterns(
        self,
        pattern_type: Optional[str] = None,
    ) -> ResearchReport:
        """
        Find design patterns in the codebase.
        
        Args:
            pattern_type: Specific pattern to look for
            
        Returns:
            ResearchReport on patterns found
        """
        query = f"design pattern {pattern_type}" if pattern_type else "design pattern implementation"
        
        results = self.vectordb.search(
            query=query,
            collection=self.vectordb_collection,
            top_k=10,
        )
        
        context_parts = []
        sources = []
        
        for r in results:
            source_info = {
                "file": r.document.metadata.get("source", "unknown"),
                "score": r.score,
            }
            sources.append(source_info)
            context_parts.append(
                f"File: {source_info['file']}\n```\n{r.document.content}\n```"
            )
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Analyze the following code samples and identify design patterns.

For each pattern found:
1. Name of the pattern
2. Where it's implemented (file and location)
3. How well it's implemented
4. Any suggestions for improvement

Code samples:
{context}"""
        
        response = self._call_llm(prompt)
        
        return ResearchReport(
            topic=f"Pattern Analysis: {pattern_type or 'All'}",
            summary=self._extract_summary(response),
            findings=self._extract_findings(response),
            recommendations=self._extract_recommendations(response),
            sources=sources,
        )
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM."""
        provider = self.llm_config.get("provider", "ollama")
        
        try:
            if provider == "ollama":
                import ollama
                response = ollama.chat(
                    model=self.llm_config.get("model", "llama3.2"),
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )
                return response["message"]["content"]
            elif provider == "openai":
                import openai
                client = openai.OpenAI(api_key=self.llm_config.get("api_key"))
                response = client.chat.completions.create(
                    model=self.llm_config.get("model", "gpt-4-turbo-preview"),
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )
                return response.choices[0].message.content
            else:
                return f"Provider {provider} not supported"
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"Error: {e}"
    
    def _extract_summary(self, response: str) -> str:
        """Extract summary from response."""
        lines = response.split("\n")
        summary_lines = []
        for line in lines[:5]:
            if line.strip():
                summary_lines.append(line.strip())
        return " ".join(summary_lines)
    
    def _extract_findings(self, response: str) -> List[Dict[str, Any]]:
        """Extract findings from response."""
        findings = []
        lines = response.split("\n")
        current_finding = None
        
        for line in lines:
            if line.strip().startswith(("-", "*", "•")) or (
                line.strip() and line.strip()[0].isdigit() and "." in line
            ):
                if current_finding:
                    findings.append({"description": current_finding})
                current_finding = line.strip().lstrip("-*•0123456789. ")
            elif current_finding and line.strip():
                current_finding += " " + line.strip()
        
        if current_finding:
            findings.append({"description": current_finding})
        
        return findings[:10]  # Limit to top 10
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from response."""
        recommendations = []
        in_recommendations = False
        
        for line in response.split("\n"):
            line_lower = line.lower()
            if "recommend" in line_lower or "suggest" in line_lower or "improve" in line_lower:
                in_recommendations = True
            
            if in_recommendations and line.strip().startswith(("-", "*", "•")):
                recommendations.append(line.strip().lstrip("-*• "))
        
        return recommendations[:5]  # Top 5 recommendations
