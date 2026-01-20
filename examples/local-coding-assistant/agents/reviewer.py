"""
Code Review Agent.

Provides automated code review with focus on quality,
security, performance, and best practices.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class Severity(str, Enum):
    """Review item severity."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ReviewItem:
    """A single review finding."""
    
    title: str
    description: str
    severity: Severity
    category: str  # security, performance, style, logic, etc.
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    code_sample: Optional[str] = None


@dataclass
class CodeReview:
    """Complete code review result."""
    
    file_path: str
    summary: str
    items: List[ReviewItem] = field(default_factory=list)
    passed: bool = True
    score: float = 100.0  # 0-100
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReviewerAgent:
    """
    Code review specialist agent.
    
    Reviews code for quality, security, performance,
    and adherence to best practices.
    
    Example:
        >>> agent = ReviewerAgent()
        >>> review = agent.review_code(code, language="python")
        >>> for item in review.items:
        ...     print(f"{item.severity}: {item.title}")
    """
    
    DEFAULT_SYSTEM_PROMPT = """You are an experienced code reviewer. Review code for:
- Correctness and logic errors
- Security vulnerabilities
- Performance issues
- Code style and readability
- Test coverage considerations
- Error handling

Provide actionable feedback with specific suggestions.

For each issue found, specify:
1. The severity (critical, high, medium, low, info)
2. The category (security, performance, logic, style, etc.)
3. A clear description of the issue
4. A specific suggestion for fixing it"""
    
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        strict_mode: bool = False,
    ):
        """
        Initialize the reviewer agent.
        
        Args:
            system_prompt: Custom system prompt
            llm_config: LLM configuration
            strict_mode: Enable stricter review criteria
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm_config = llm_config or {}
        self.strict_mode = strict_mode
    
    def review_code(
        self,
        code: str,
        language: str = "python",
        focus: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> CodeReview:
        """
        Review a piece of code.
        
        Args:
            code: Code to review
            language: Programming language
            focus: Areas to focus on
            context: Additional context about the code
            
        Returns:
            CodeReview with findings
        """
        focus_areas = focus or ["security", "performance", "style", "logic"]
        focus_str = ", ".join(focus_areas)
        
        context_section = f"\nContext: {context}" if context else ""
        strict_note = "\nApply strict review criteria." if self.strict_mode else ""
        
        prompt = f"""Review this {language} code focusing on: {focus_str}{context_section}{strict_note}

```{language}
{code}
```

For each issue found, provide in this exact format:
ISSUE: [title]
SEVERITY: [critical/high/medium/low/info]
CATEGORY: [security/performance/logic/style/error-handling/other]
DESCRIPTION: [detailed description]
SUGGESTION: [how to fix]
LINE: [line number if applicable, or N/A]

After all issues, provide:
SUMMARY: [overall assessment]
SCORE: [0-100 quality score]"""
        
        response = self._call_llm(prompt)
        
        # Parse response
        items = self._parse_review_items(response)
        summary = self._extract_summary(response)
        score = self._extract_score(response)
        
        # Determine if passed
        critical_count = sum(1 for i in items if i.severity == Severity.CRITICAL)
        high_count = sum(1 for i in items if i.severity == Severity.HIGH)
        passed = critical_count == 0 and (high_count < 3 or not self.strict_mode)
        
        return CodeReview(
            file_path="inline",
            summary=summary,
            items=items,
            passed=passed,
            score=score,
            metadata={
                "language": language,
                "focus": focus_areas,
                "strict_mode": self.strict_mode,
            },
        )
    
    def review_file(
        self,
        file_path: str,
        focus: Optional[List[str]] = None,
    ) -> CodeReview:
        """
        Review a file.
        
        Args:
            file_path: Path to file
            focus: Areas to focus on
            
        Returns:
            CodeReview with findings
        """
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            return CodeReview(
                file_path=file_path,
                summary="File not found",
                passed=False,
                score=0,
            )
        
        code = path.read_text(encoding="utf-8", errors="ignore")
        language = self._detect_language(path.suffix)
        
        review = self.review_code(
            code=code,
            language=language,
            focus=focus,
            context=f"File: {file_path}",
        )
        review.file_path = file_path
        
        return review
    
    def quick_check(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Perform a quick code check.
        
        Args:
            code: Code to check
            language: Programming language
            
        Returns:
            Quick check results
        """
        prompt = f"""Quickly check this {language} code for major issues only.

```{language}
{code}
```

List only CRITICAL or HIGH severity issues in one line each.
Format: [SEVERITY]: [brief description]

If no major issues, respond with: No major issues found."""
        
        response = self._call_llm(prompt)
        
        issues = []
        for line in response.split("\n"):
            if "CRITICAL" in line or "HIGH" in line:
                issues.append(line.strip())
        
        return {
            "has_major_issues": len(issues) > 0,
            "issues": issues,
            "passed": len(issues) == 0,
        }
    
    def security_review(
        self,
        code: str,
        language: str = "python",
    ) -> CodeReview:
        """
        Perform security-focused review.
        
        Args:
            code: Code to review
            language: Programming language
            
        Returns:
            Security-focused CodeReview
        """
        prompt = f"""Perform a security-focused code review of this {language} code.

```{language}
{code}
```

Check for:
1. SQL Injection vulnerabilities
2. Cross-site scripting (XSS)
3. Authentication/authorization issues
4. Sensitive data exposure
5. Input validation problems
6. Insecure cryptography
7. Path traversal
8. Command injection
9. Hardcoded secrets
10. Insecure configurations

For each vulnerability found:
VULN: [name]
SEVERITY: [critical/high/medium/low]
DESCRIPTION: [how it can be exploited]
FIX: [how to fix it]"""
        
        response = self._call_llm(prompt)
        items = self._parse_security_items(response)
        
        critical = sum(1 for i in items if i.severity == Severity.CRITICAL)
        high = sum(1 for i in items if i.severity == Severity.HIGH)
        
        score = max(0, 100 - (critical * 30) - (high * 15))
        
        return CodeReview(
            file_path="inline",
            summary=f"Found {len(items)} security issues ({critical} critical, {high} high)",
            items=items,
            passed=critical == 0,
            score=score,
            metadata={"review_type": "security"},
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
    
    def _parse_review_items(self, response: str) -> List[ReviewItem]:
        """Parse review items from LLM response."""
        items = []
        current = {}
        
        for line in response.split("\n"):
            line = line.strip()
            
            if line.startswith("ISSUE:"):
                if current.get("title"):
                    items.append(self._create_item(current))
                current = {"title": line[6:].strip()}
            elif line.startswith("SEVERITY:"):
                current["severity"] = line[9:].strip().lower()
            elif line.startswith("CATEGORY:"):
                current["category"] = line[9:].strip().lower()
            elif line.startswith("DESCRIPTION:"):
                current["description"] = line[12:].strip()
            elif line.startswith("SUGGESTION:"):
                current["suggestion"] = line[11:].strip()
            elif line.startswith("LINE:"):
                line_val = line[5:].strip()
                if line_val.isdigit():
                    current["line_number"] = int(line_val)
        
        if current.get("title"):
            items.append(self._create_item(current))
        
        return items
    
    def _parse_security_items(self, response: str) -> List[ReviewItem]:
        """Parse security findings from response."""
        items = []
        current = {}
        
        for line in response.split("\n"):
            line = line.strip()
            
            if line.startswith("VULN:"):
                if current.get("title"):
                    items.append(self._create_security_item(current))
                current = {"title": line[5:].strip()}
            elif line.startswith("SEVERITY:"):
                current["severity"] = line[9:].strip().lower()
            elif line.startswith("DESCRIPTION:"):
                current["description"] = line[12:].strip()
            elif line.startswith("FIX:"):
                current["suggestion"] = line[4:].strip()
        
        if current.get("title"):
            items.append(self._create_security_item(current))
        
        return items
    
    def _create_item(self, data: Dict[str, Any]) -> ReviewItem:
        """Create ReviewItem from parsed data."""
        try:
            severity = Severity(data.get("severity", "info"))
        except ValueError:
            severity = Severity.INFO
        
        return ReviewItem(
            title=data.get("title", "Unknown"),
            description=data.get("description", ""),
            severity=severity,
            category=data.get("category", "other"),
            line_number=data.get("line_number"),
            suggestion=data.get("suggestion"),
        )
    
    def _create_security_item(self, data: Dict[str, Any]) -> ReviewItem:
        """Create security ReviewItem."""
        try:
            severity = Severity(data.get("severity", "medium"))
        except ValueError:
            severity = Severity.MEDIUM
        
        return ReviewItem(
            title=data.get("title", "Unknown"),
            description=data.get("description", ""),
            severity=severity,
            category="security",
            suggestion=data.get("suggestion"),
        )
    
    def _extract_summary(self, response: str) -> str:
        """Extract summary from response."""
        for line in response.split("\n"):
            if line.strip().startswith("SUMMARY:"):
                return line[8:].strip()
        return "Review complete"
    
    def _extract_score(self, response: str) -> float:
        """Extract score from response."""
        for line in response.split("\n"):
            if line.strip().startswith("SCORE:"):
                try:
                    score_str = line[6:].strip().replace("%", "")
                    return float(score_str)
                except ValueError:
                    pass
        return 70.0  # Default score
    
    def _detect_language(self, suffix: str) -> str:
        """Detect language from file suffix."""
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
        }
        return mapping.get(suffix.lower(), "text")
