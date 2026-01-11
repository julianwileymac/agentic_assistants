"""
Component Generation API Router.

This module provides REST endpoints for AI-powered component generation:
- Generate components from user notes using two-stage LLM
- Create optimized prompts from freeform notes
- Generate component code from refined prompts
"""

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GeneratePromptRequest(BaseModel):
    """Request to generate an optimized prompt from notes."""
    notes: str = Field(..., description="Freeform notes describing the component")
    component_type: str = Field(default="tool", description="Type of component to generate")
    additional_context: Optional[str] = Field(default=None, description="Additional context")


class GeneratePromptResponse(BaseModel):
    """Response with the optimized prompt."""
    original_notes: str
    optimized_prompt: str
    component_type: str
    suggestions: List[str] = Field(default_factory=list)


class GenerateComponentRequest(BaseModel):
    """Request to generate a component from a prompt."""
    prompt: str = Field(..., description="Prompt for component generation")
    component_type: str = Field(default="tool", description="Type of component")
    name: Optional[str] = Field(default=None, description="Suggested component name")
    language: str = Field(default="python", description="Programming language")


class GenerateComponentResponse(BaseModel):
    """Response with generated component."""
    name: str
    category: str
    code: str
    description: str
    usage_example: str
    language: str
    tags: List[str]


class GenerateFromNotesRequest(BaseModel):
    """Request to generate a component directly from notes (two-stage)."""
    notes: str = Field(..., description="Freeform notes describing the component")
    component_type: str = Field(default="tool", description="Type of component")
    name: Optional[str] = Field(default=None, description="Suggested component name")
    language: str = Field(default="python", description="Programming language")
    save_component: bool = Field(default=False, description="Save the generated component")


class GenerateFromNotesResponse(BaseModel):
    """Response with full generation result."""
    optimized_prompt: str
    component: GenerateComponentResponse
    saved: bool = False
    component_id: Optional[str] = None


class ChatMessage(BaseModel):
    """A message in the generation chat."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class GenerationChatRequest(BaseModel):
    """Request for multi-turn generation chat."""
    messages: List[ChatMessage] = Field(..., description="Chat history")
    component_type: str = Field(default="tool", description="Type of component")


class GenerationChatResponse(BaseModel):
    """Response from generation chat."""
    message: ChatMessage
    component_preview: Optional[GenerateComponentResponse] = None
    suggestions: List[str] = Field(default_factory=list)


# ============================================================================
# Prompt Templates
# ============================================================================

PROMPT_OPTIMIZATION_TEMPLATE = """You are an expert at converting freeform notes into clear, structured prompts for code generation.

Given the following notes about a {component_type} component:

---
{notes}
---

Additional context (if any): {context}

Create an optimized, detailed prompt that would help an AI code generator create this {component_type} component. The prompt should:
1. Clearly describe what the component should do
2. List the main functions/methods needed
3. Specify input/output types
4. Note any dependencies or integrations required
5. Include any error handling requirements

Output only the optimized prompt, nothing else."""

CODE_GENERATION_TEMPLATE = """You are an expert {language} developer specializing in AI/ML and agentic systems.

Generate a complete, production-ready {component_type} component based on this description:

---
{prompt}
---

Requirements:
1. Write clean, well-documented {language} code
2. Include type hints and docstrings
3. Follow best practices for the component type
4. Make the code modular and reusable
5. Include error handling where appropriate

Output format:
1. First, output the main code in a code block
2. Then, provide a brief description (1-2 sentences)
3. Finally, provide a usage example in a code block

Component name suggestion: {name}"""

COMPONENT_NAME_TEMPLATE = """Based on these notes, suggest a concise, descriptive name for a {component_type} component:

Notes: {notes}

Output only the component name in CamelCase (e.g., DocumentRetriever, TaskScheduler)."""


# ============================================================================
# LLM Helper
# ============================================================================

class OllamaClient:
    """Simple Ollama client for generation."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self.host = self.config.ollama.host
        self.model = self.config.ollama.default_model
        self.timeout = self.config.ollama.timeout
    
    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Ollama.
        
        Args:
            prompt: The prompt to generate from
            model: Optional model override
        
        Returns:
            Generated text
        """
        import httpx
        
        model = model or self.model
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail=f"Ollama request timed out after {self.timeout}s"
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama request failed: {str(e)}"
            )
    
    async def chat(self, messages: List[dict], model: Optional[str] = None) -> str:
        """Chat with Ollama.
        
        Args:
            messages: List of message dicts with role and content
            model: Optional model override
        
        Returns:
            Assistant's response
        """
        import httpx
        
        model = model or self.model
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail=f"Ollama request timed out after {self.timeout}s"
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama request failed: {str(e)}"
            )


_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get the Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


# ============================================================================
# Code Parsing Helpers
# ============================================================================

def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from markdown-formatted text."""
    import re
    
    # Match code blocks with optional language specifier
    pattern = r'```(?:\w+)?\n(.*?)```'
    blocks = re.findall(pattern, text, re.DOTALL)
    
    return [block.strip() for block in blocks]


def parse_generation_output(text: str, component_type: str) -> dict:
    """Parse the generation output into structured data."""
    code_blocks = extract_code_blocks(text)
    
    # Main code is usually the first/longest block
    code = code_blocks[0] if code_blocks else ""
    
    # Usage example is usually the second block
    usage_example = code_blocks[1] if len(code_blocks) > 1 else ""
    
    # Extract description (text between code blocks)
    import re
    description_match = re.search(r'```.*?```\s*(.+?)\s*(?:```|$)', text, re.DOTALL)
    description = description_match.group(1).strip() if description_match else ""
    
    # If no description found, try to extract from before first code block
    if not description:
        before_code = text.split('```')[0].strip()
        if before_code:
            description = before_code[:500]
    
    return {
        "code": code,
        "description": description[:500],
        "usage_example": usage_example,
    }


def suggest_tags(code: str, component_type: str) -> List[str]:
    """Suggest tags based on code content."""
    tags = [component_type]
    
    # Common patterns
    patterns = {
        "async": ["async", "asyncio"],
        "class ": ["oop", "class"],
        "httpx": ["http", "api"],
        "requests": ["http", "api"],
        "pandas": ["data", "pandas"],
        "numpy": ["numpy", "data"],
        "langchain": ["langchain", "llm"],
        "crewai": ["crewai", "agent"],
        "llama": ["llama-index", "rag"],
        "openai": ["openai", "llm"],
        "ollama": ["ollama", "local-llm"],
        "chromadb": ["chromadb", "vector"],
        "lancedb": ["lancedb", "vector"],
        "mlflow": ["mlflow", "tracking"],
    }
    
    code_lower = code.lower()
    for pattern, tag_list in patterns.items():
        if pattern in code_lower:
            tags.extend(tag_list)
    
    return list(set(tags))[:10]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/prompt", response_model=GeneratePromptResponse)
async def generate_optimized_prompt(request: GeneratePromptRequest) -> GeneratePromptResponse:
    """Generate an optimized prompt from freeform notes."""
    client = get_ollama_client()
    
    prompt = PROMPT_OPTIMIZATION_TEMPLATE.format(
        component_type=request.component_type,
        notes=request.notes,
        context=request.additional_context or "None",
    )
    
    optimized = await client.generate(prompt)
    
    # Generate suggestions
    suggestions = [
        "Consider adding error handling",
        "Include type hints for better maintainability",
        "Add usage examples in the docstring",
    ]
    
    return GeneratePromptResponse(
        original_notes=request.notes,
        optimized_prompt=optimized.strip(),
        component_type=request.component_type,
        suggestions=suggestions,
    )


@router.post("/component", response_model=GenerateComponentResponse)
async def generate_component(request: GenerateComponentRequest) -> GenerateComponentResponse:
    """Generate a component from a prompt."""
    client = get_ollama_client()
    
    # Generate name if not provided
    name = request.name
    if not name:
        name_prompt = COMPONENT_NAME_TEMPLATE.format(
            component_type=request.component_type,
            notes=request.prompt[:500],
        )
        name = await client.generate(name_prompt)
        name = name.strip().replace(" ", "")
    
    # Generate code
    code_prompt = CODE_GENERATION_TEMPLATE.format(
        language=request.language,
        component_type=request.component_type,
        prompt=request.prompt,
        name=name,
    )
    
    generated = await client.generate(code_prompt)
    parsed = parse_generation_output(generated, request.component_type)
    tags = suggest_tags(parsed["code"], request.component_type)
    
    return GenerateComponentResponse(
        name=name,
        category=request.component_type,
        code=parsed["code"],
        description=parsed["description"],
        usage_example=parsed["usage_example"],
        language=request.language,
        tags=tags,
    )


@router.post("/from-notes", response_model=GenerateFromNotesResponse)
async def generate_from_notes(request: GenerateFromNotesRequest) -> GenerateFromNotesResponse:
    """Generate a component from notes using two-stage LLM pipeline."""
    client = get_ollama_client()
    
    # Stage 1: Optimize the prompt
    opt_prompt = PROMPT_OPTIMIZATION_TEMPLATE.format(
        component_type=request.component_type,
        notes=request.notes,
        context="None",
    )
    optimized_prompt = await client.generate(opt_prompt)
    optimized_prompt = optimized_prompt.strip()
    
    # Generate name if not provided
    name = request.name
    if not name:
        name_prompt = COMPONENT_NAME_TEMPLATE.format(
            component_type=request.component_type,
            notes=request.notes[:500],
        )
        name = await client.generate(name_prompt)
        name = name.strip().replace(" ", "").replace('"', '').replace("'", "")
    
    # Stage 2: Generate the component
    code_prompt = CODE_GENERATION_TEMPLATE.format(
        language=request.language,
        component_type=request.component_type,
        prompt=optimized_prompt,
        name=name,
    )
    
    generated = await client.generate(code_prompt)
    parsed = parse_generation_output(generated, request.component_type)
    tags = suggest_tags(parsed["code"], request.component_type)
    
    component = GenerateComponentResponse(
        name=name,
        category=request.component_type,
        code=parsed["code"],
        description=parsed["description"],
        usage_example=parsed["usage_example"],
        language=request.language,
        tags=tags,
    )
    
    # Save if requested
    saved = False
    component_id = None
    
    if request.save_component and parsed["code"]:
        try:
            store = ControlPanelStore.get_instance()
            saved_component = store.create_component(
                name=name,
                category=request.component_type,
                code=parsed["code"],
                language=request.language,
                description=parsed["description"],
                usage_example=parsed["usage_example"],
                tags=tags,
                metadata={"generated": True, "source": "notes"},
            )
            saved = True
            component_id = saved_component.id
        except Exception as e:
            logger.error(f"Failed to save component: {e}")
    
    return GenerateFromNotesResponse(
        optimized_prompt=optimized_prompt,
        component=component,
        saved=saved,
        component_id=component_id,
    )


@router.post("/chat", response_model=GenerationChatResponse)
async def generation_chat(request: GenerationChatRequest) -> GenerationChatResponse:
    """Multi-turn chat for component generation refinement."""
    client = get_ollama_client()
    
    # Build system message
    system_message = {
        "role": "system",
        "content": f"""You are a helpful AI assistant specializing in generating {request.component_type} components for an agentic AI platform.

Help the user refine their component idea. Ask clarifying questions, suggest improvements, and when the user is ready, generate the component code.

When generating code:
1. Use proper Python conventions
2. Include docstrings and type hints
3. Make the code production-ready
4. Suggest relevant tags for the component

If the user's message indicates they want to generate code, output the code in a markdown code block.""",
    }
    
    # Build messages for Ollama
    messages = [system_message]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Generate response
    response_text = await client.chat(messages)
    
    # Check if response contains code
    code_blocks = extract_code_blocks(response_text)
    component_preview = None
    
    if code_blocks:
        parsed = parse_generation_output(response_text, request.component_type)
        tags = suggest_tags(parsed["code"], request.component_type)
        
        component_preview = GenerateComponentResponse(
            name="GeneratedComponent",
            category=request.component_type,
            code=parsed["code"],
            description=parsed["description"],
            usage_example=parsed["usage_example"],
            language="python",
            tags=tags,
        )
    
    # Suggest next steps
    suggestions = []
    if not code_blocks:
        suggestions = [
            "Tell me more about the component's purpose",
            "What inputs and outputs should it have?",
            "Generate the code when ready",
        ]
    else:
        suggestions = [
            "Save this component",
            "Refine the code",
            "Add more features",
        ]
    
    return GenerationChatResponse(
        message=ChatMessage(role="assistant", content=response_text),
        component_preview=component_preview,
        suggestions=suggestions,
    )


@router.post("/from-note/{note_id}", response_model=GenerateFromNotesResponse)
async def generate_from_note_id(
    note_id: str,
    component_type: str = Query(default="tool", description="Type of component"),
    save_component: bool = Query(default=False, description="Save the generated component"),
) -> GenerateFromNotesResponse:
    """Generate a component from an existing note."""
    store = ControlPanelStore.get_instance()
    
    # Get all notes and find the one with matching ID
    # Notes are stored per resource, so we need to search
    from agentic_assistants.core.models import Note
    
    # Try to find the note by querying with the ID
    with store._get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note_content = row["content"]
    
    # Generate using the note content
    request = GenerateFromNotesRequest(
        notes=note_content,
        component_type=component_type,
        save_component=save_component,
    )
    
    return await generate_from_notes(request)



