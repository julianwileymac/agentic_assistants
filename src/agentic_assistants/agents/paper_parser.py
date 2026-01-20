"""
Paper Parser Agent for extracting learning topics from research papers.

Uses Ollama to analyze research papers and extract:
- Key concepts and topics
- Learning objectives
- Suggested lesson structures
"""

import json
import re
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


PAPER_PARSER_SYSTEM_PROMPT = """You are an expert at analyzing academic and technical content.
Your task is to identify learnable topics and concepts from research papers, articles, and technical documents.

When analyzing content:
1. Identify the main topics and concepts
2. Extract key terminology and definitions
3. Recognize the logical structure and dependencies between concepts
4. Assess difficulty levels for different concepts
5. Suggest practical applications and learning objectives

Focus on extracting information that would be useful for creating learning materials."""


PAPER_ANALYSIS_TEMPLATE = """Analyze the following document and extract learnable topics.

Title: {title}

Content:
{content}

Please analyze this document and identify topics suitable for learning. Return your analysis in JSON format:
{{
    "summary": "A concise summary of the document (2-3 sentences)",
    "main_topic": "The primary topic or theme",
    "topics": [
        {{
            "name": "Topic name",
            "description": "Brief description of what this topic covers",
            "key_concepts": ["Concept 1", "Concept 2", ...],
            "difficulty": "beginner|intermediate|advanced|expert",
            "prerequisites": ["Prerequisite topic 1", ...],
            "estimated_learning_hours": <float>,
            "confidence": <0.0-1.0 confidence that this is a learnable topic>
        }}
    ],
    "key_terms": [
        {{"term": "Term", "definition": "Definition"}}
    ],
    "suggested_learning_path": ["Topic 1", "Topic 2", ...],
    "practical_applications": ["Application 1", ...],
    "related_fields": ["Field 1", ...]
}}

Extract 3-7 learnable topics from the content. Focus on concepts that can be taught and learned independently."""


class PaperParserAgent:
    """
    Agent for parsing research papers and extracting learning topics.
    
    This agent:
    - Analyzes document content
    - Extracts key topics and concepts
    - Identifies learning objectives
    - Suggests difficulty levels and prerequisites
    - Provides summaries and key term definitions
    
    Example:
        >>> parser = PaperParserAgent()
        >>> result = parser.parse(
        ...     text="Full paper content...",
        ...     title="Introduction to Neural Networks"
        ... )
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the paper parser agent.
        
        Args:
            config: Agentic configuration instance
            model: Ollama model to use
            system_prompt: Custom system prompt
        """
        self.config = config or AgenticConfig()
        self.model = model or self.config.ollama.default_model
        self.system_prompt = system_prompt or PAPER_PARSER_SYSTEM_PROMPT
        self._ollama = OllamaManager(self.config)
    
    def parse(
        self,
        text: str,
        title: Optional[str] = None,
        max_length: int = 15000,
    ) -> Dict[str, Any]:
        """
        Parse a document and extract learning topics.
        
        Args:
            text: The document text content
            title: Optional title of the document
            max_length: Maximum text length to process
        
        Returns:
            Dictionary with extracted topics and analysis
        """
        logger.info(f"Parsing document: {title or 'Untitled'}")
        
        # Truncate if too long
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length] + "\n\n[Content truncated...]"
        
        prompt = PAPER_ANALYSIS_TEMPLATE.format(
            title=title or "Untitled Document",
            content=text,
        )
        
        try:
            self._ollama.ensure_running()
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(
                messages=messages,
                model=self.model,
            )
            
            response_text = response.get("message", {}).get("content", "")
            
            # Parse result
            result = self._parse_analysis(response_text)
            
            logger.info(f"Extracted {len(result.get('topics', []))} topics")
            
            return result
            
        except Exception as e:
            logger.error(f"Paper parsing failed: {e}")
            return self._create_fallback_analysis(text, title)
    
    def _parse_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse the analysis JSON from the LLM response."""
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if json_match:
            try:
                result = json.loads(json_match.group())
                return self._validate_result(result)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse analysis JSON: {e}")
        
        return self._extract_analysis_from_text(response_text)
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the analysis result."""
        defaults = {
            "summary": "",
            "main_topic": "General Topic",
            "topics": [],
            "key_terms": [],
            "suggested_learning_path": [],
            "practical_applications": [],
            "related_fields": [],
        }
        
        for key, default in defaults.items():
            if key not in result:
                result[key] = default
        
        # Validate topics
        valid_topics = []
        for topic in result.get("topics", []):
            if isinstance(topic, dict) and topic.get("name"):
                # Ensure required fields
                topic.setdefault("description", "")
                topic.setdefault("key_concepts", [])
                topic.setdefault("difficulty", "intermediate")
                topic.setdefault("prerequisites", [])
                topic.setdefault("estimated_learning_hours", 2.0)
                topic.setdefault("confidence", 0.7)
                valid_topics.append(topic)
        
        result["topics"] = valid_topics
        
        return result
    
    def _extract_analysis_from_text(self, text: str) -> Dict[str, Any]:
        """Extract analysis from unstructured text."""
        # Basic extraction when JSON parsing fails
        topics = []
        
        # Look for topic-like patterns
        topic_patterns = [
            r'Topic:?\s*(.+?)(?:\n|$)',
            r'\d+\.\s*(.+?)(?:\n|$)',
            r'•\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:5]:  # Limit to 5 topics
                if len(match) > 5 and len(match) < 200:
                    topics.append({
                        "name": match.strip(),
                        "description": "",
                        "key_concepts": [],
                        "difficulty": "intermediate",
                        "prerequisites": [],
                        "estimated_learning_hours": 2.0,
                        "confidence": 0.5,
                    })
        
        # If no topics found, create a generic one
        if not topics:
            topics = [{
                "name": "Main Topic",
                "description": text[:200] if text else "",
                "key_concepts": [],
                "difficulty": "intermediate",
                "prerequisites": [],
                "estimated_learning_hours": 2.0,
                "confidence": 0.3,
            }]
        
        return {
            "summary": text[:300] if text else "",
            "main_topic": topics[0]["name"] if topics else "Unknown",
            "topics": topics,
            "key_terms": [],
            "suggested_learning_path": [t["name"] for t in topics],
            "practical_applications": [],
            "related_fields": [],
        }
    
    def _create_fallback_analysis(
        self,
        text: str,
        title: Optional[str],
    ) -> Dict[str, Any]:
        """Create a fallback analysis when parsing fails."""
        # Extract some basic info from the text
        words = text.split()
        word_count = len(words)
        
        # Simple topic extraction based on common words
        topics = [{
            "name": title or "Imported Topic",
            "description": f"Topic extracted from document with {word_count} words",
            "key_concepts": [],
            "difficulty": "intermediate",
            "prerequisites": [],
            "estimated_learning_hours": max(1.0, word_count / 1000),
            "confidence": 0.3,
        }]
        
        return {
            "summary": text[:300] + "..." if len(text) > 300 else text,
            "main_topic": title or "Imported Document",
            "topics": topics,
            "key_terms": [],
            "suggested_learning_path": [title or "Main Topic"],
            "practical_applications": [],
            "related_fields": [],
        }
    
    def extract_key_terms(
        self,
        text: str,
        max_terms: int = 20,
    ) -> List[Dict[str, str]]:
        """
        Extract key terms and their definitions from text.
        
        Args:
            text: Document text
            max_terms: Maximum number of terms to extract
        
        Returns:
            List of dictionaries with term and definition
        """
        prompt = f"""Extract key technical terms and their definitions from this text.
Return up to {max_terms} terms as a JSON array:

Text:
{text[:10000]}

Return format:
[
    {{"term": "Term name", "definition": "Clear, concise definition"}}
]

Focus on domain-specific terminology that a learner would need to understand."""

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(messages=messages, model=self.model)
            response_text = response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                terms = json.loads(json_match.group())
                return terms[:max_terms]
        except Exception as e:
            logger.error(f"Term extraction failed: {e}")
        
        return []
    
    def suggest_learning_objectives(
        self,
        topic: Dict[str, Any],
    ) -> List[str]:
        """
        Generate learning objectives for a topic.
        
        Args:
            topic: Topic dictionary with name and description
        
        Returns:
            List of learning objectives
        """
        prompt = f"""Generate clear, measurable learning objectives for this topic.

Topic: {topic.get('name', '')}
Description: {topic.get('description', '')}
Difficulty: {topic.get('difficulty', 'intermediate')}

Return 4-6 learning objectives as a JSON array of strings.
Use action verbs (understand, apply, analyze, create, evaluate).
Format: ["Objective 1", "Objective 2", ...]"""

        try:
            messages = [
                {"role": "system", "content": "You are an expert at creating educational objectives."},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(messages=messages, model=self.model)
            response_text = response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Objective generation failed: {e}")
        
        # Fallback objectives
        return [
            f"Understand the fundamentals of {topic.get('name', 'the topic')}",
            "Apply key concepts to practical scenarios",
            "Analyze and evaluate related problems",
        ]
    
    def chunk_for_vector_storage(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Chunk document text for vector database storage.
        
        Args:
            text: Full document text
            chunk_size: Target size for each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "index": chunk_index,
                        "char_start": len("".join(c["text"] for c in chunks)),
                        "char_end": len("".join(c["text"] for c in chunks)) + len(current_chunk),
                    })
                    chunk_index += 1
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "index": chunk_index,
                "char_start": len("".join(c["text"] for c in chunks)),
                "char_end": len("".join(c["text"] for c in chunks)) + len(current_chunk),
            })
        
        logger.info(f"Created {len(chunks)} chunks from document")
        
        return chunks
    
    def summarize_section(
        self,
        text: str,
        max_length: int = 200,
    ) -> str:
        """
        Generate a concise summary of a text section.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in characters
        
        Returns:
            Summary string
        """
        prompt = f"""Summarize this text in {max_length} characters or less:

{text[:5000]}

Provide a clear, informative summary that captures the key points."""

        try:
            messages = [
                {"role": "system", "content": "You are an expert at creating concise, accurate summaries."},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(messages=messages, model=self.model)
            summary = response.get("message", {}).get("content", "")
            
            # Truncate if needed
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return text[:max_length-3] + "..." if len(text) > max_length else text
