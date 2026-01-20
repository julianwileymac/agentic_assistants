"""
Upload API Router.

This module provides REST endpoints for document upload and remote fetching:
- File upload (single and multiple)
- Directory upload (as zip)
- Remote URL fetching
- GitHub repository fetching
- S3/MinIO fetching
"""

import hashlib
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


# ============================================================================
# Request/Response Models
# ============================================================================

class UploadResponse(BaseModel):
    """Response from file upload."""
    success: bool
    file_id: str
    filename: str
    size_bytes: int
    content_type: str
    path: str
    metadata: dict = Field(default_factory=dict)


class MultiUploadResponse(BaseModel):
    """Response from multiple file upload."""
    success: bool
    files: List[UploadResponse]
    total_files: int
    total_size_bytes: int
    errors: List[str] = Field(default_factory=list)


class FetchUrlRequest(BaseModel):
    """Request to fetch from URL."""
    url: str = Field(..., description="URL to fetch")
    filename: Optional[str] = Field(default=None, description="Override filename")
    collection: Optional[str] = Field(default=None, description="Target collection")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    tags: List[str] = Field(default_factory=list, description="Tags for the document")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    process_immediately: bool = Field(default=False, description="Process and index immediately")


class FetchGitHubRequest(BaseModel):
    """Request to fetch from GitHub."""
    repo_url: str = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Branch to fetch")
    paths: List[str] = Field(default_factory=list, description="Specific paths to fetch (empty = all)")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: ["*.pyc", "__pycache__", "node_modules", ".git"],
        description="Patterns to exclude",
    )
    collection: Optional[str] = Field(default=None, description="Target collection")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    tags: List[str] = Field(default_factory=list, description="Tags for documents")
    process_immediately: bool = Field(default=False, description="Process and index immediately")


class FetchS3Request(BaseModel):
    """Request to fetch from S3/MinIO."""
    bucket: str = Field(..., description="S3 bucket name")
    prefix: str = Field(default="", description="Key prefix (folder)")
    keys: List[str] = Field(default_factory=list, description="Specific keys to fetch (empty = all in prefix)")
    endpoint_url: Optional[str] = Field(default=None, description="Custom S3 endpoint (for MinIO)")
    collection: Optional[str] = Field(default=None, description="Target collection")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    tags: List[str] = Field(default_factory=list, description="Tags for documents")
    process_immediately: bool = Field(default=False, description="Process and index immediately")


class FetchResponse(BaseModel):
    """Response from fetch operations."""
    success: bool
    source: str
    files_fetched: int
    total_size_bytes: int
    file_paths: List[str]
    errors: List[str] = Field(default_factory=list)
    job_id: Optional[str] = Field(default=None, description="Job ID if processing async")


class ProcessingStatus(BaseModel):
    """Status of document processing."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0-100
    files_processed: int
    total_files: int
    errors: List[str] = Field(default_factory=list)
    result: Optional[dict] = None


# ============================================================================
# Helper Functions
# ============================================================================

_config: Optional[AgenticConfig] = None


def get_config() -> AgenticConfig:
    """Get configuration instance."""
    global _config
    if _config is None:
        _config = AgenticConfig()
    return _config


def get_upload_dir() -> Path:
    """Get the upload directory."""
    config = get_config()
    upload_dir = config.data_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def generate_file_id(filename: str, content: bytes = None) -> str:
    """Generate a unique file ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if content:
        content_hash = hashlib.sha256(content[:1024]).hexdigest()[:8]
        return f"{timestamp}_{content_hash}_{Path(filename).stem}"
    return f"{timestamp}_{uuid4().hex[:8]}_{Path(filename).stem}"


def get_content_type(filename: str) -> str:
    """Get content type from filename."""
    import mimetypes
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


# ============================================================================
# File Upload Endpoints
# ============================================================================

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    collection: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    process_immediately: bool = Form(False),
) -> UploadResponse:
    """
    Upload a single file.
    
    The file is saved to the upload directory and optionally processed
    for indexing into a vector store collection.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Generate file ID and path
    file_id = generate_file_id(file.filename, content)
    upload_dir = get_upload_dir()
    
    # Create subdirectory based on date
    date_dir = upload_dir / datetime.utcnow().strftime("%Y/%m/%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_ext = Path(file.filename).suffix
    file_path = date_dir / f"{file_id}{file_ext}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Build metadata
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    metadata = {
        "original_filename": file.filename,
        "upload_timestamp": datetime.utcnow().isoformat(),
        "collection": collection,
        "project_id": project_id,
        "tags": tag_list,
    }
    
    logger.info(f"Uploaded file: {file.filename} -> {file_path}")
    
    # Process immediately if requested
    if process_immediately and collection:
        try:
            from agentic_assistants.pipelines.nodes import vectorstore_upsert_node
            
            # Read and process file content
            text_content = _extract_text_content(file_path)
            if text_content:
                result = vectorstore_upsert_node(
                    documents=[{
                        "content": text_content,
                        "metadata": {
                            **metadata,
                            "source_path": str(file_path),
                        },
                    }],
                    config={
                        "collection": collection,
                        "project_id": project_id,
                        "scope": "project" if project_id else "global",
                        "tags": tag_list,
                    },
                )
                metadata["indexed"] = result.get("success", False)
        except Exception as e:
            logger.error(f"Failed to process file: {e}")
            metadata["index_error"] = str(e)
    
    return UploadResponse(
        success=True,
        file_id=file_id,
        filename=file.filename,
        size_bytes=file_size,
        content_type=get_content_type(file.filename),
        path=str(file_path),
        metadata=metadata,
    )


@router.post("/files", response_model=MultiUploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    collection: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    process_immediately: bool = Form(False),
) -> MultiUploadResponse:
    """Upload multiple files."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    errors = []
    total_size = 0
    
    for file in files:
        try:
            result = await upload_file(
                file=file,
                collection=collection,
                project_id=project_id,
                tags=tags,
                process_immediately=process_immediately,
            )
            results.append(result)
            total_size += result.size_bytes
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return MultiUploadResponse(
        success=len(errors) == 0,
        files=results,
        total_files=len(results),
        total_size_bytes=total_size,
        errors=errors,
    )


@router.post("/directory", response_model=MultiUploadResponse)
async def upload_directory(
    file: UploadFile = File(...),
    collection: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    process_immediately: bool = Form(False),
) -> MultiUploadResponse:
    """
    Upload a directory as a zip file.
    
    The zip file is extracted and each file is processed.
    """
    import zipfile
    
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Must upload a .zip file")
    
    # Save zip to temp location
    content = await file.read()
    
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    results = []
    errors = []
    total_size = 0
    
    try:
        with zipfile.ZipFile(tmp_path, "r") as zf:
            # Extract to temp directory
            extract_dir = tempfile.mkdtemp()
            zf.extractall(extract_dir)
            
            # Process each file
            for root, _, filenames in Path(extract_dir).walk():
                for filename in filenames:
                    file_path = Path(root) / filename
                    
                    try:
                        # Read file
                        file_content = file_path.read_bytes()
                        file_size = len(file_content)
                        
                        # Generate ID and save
                        file_id = generate_file_id(filename, file_content)
                        upload_dir = get_upload_dir()
                        date_dir = upload_dir / datetime.utcnow().strftime("%Y/%m/%d")
                        date_dir.mkdir(parents=True, exist_ok=True)
                        
                        dest_path = date_dir / f"{file_id}{file_path.suffix}"
                        shutil.copy2(file_path, dest_path)
                        
                        tag_list = [t.strip() for t in tags.split(",")] if tags else []
                        
                        results.append(UploadResponse(
                            success=True,
                            file_id=file_id,
                            filename=filename,
                            size_bytes=file_size,
                            content_type=get_content_type(filename),
                            path=str(dest_path),
                            metadata={
                                "original_filename": filename,
                                "from_archive": file.filename,
                                "collection": collection,
                                "project_id": project_id,
                                "tags": tag_list,
                            },
                        ))
                        total_size += file_size
                        
                    except Exception as e:
                        errors.append(f"{filename}: {str(e)}")
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    
    return MultiUploadResponse(
        success=len(errors) == 0,
        files=results,
        total_files=len(results),
        total_size_bytes=total_size,
        errors=errors,
    )


# ============================================================================
# Remote Fetch Endpoints
# ============================================================================

@router.post("/fetch/url", response_model=FetchResponse)
async def fetch_url(request: FetchUrlRequest) -> FetchResponse:
    """Fetch document from a URL."""
    import httpx
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            response = await client.get(request.url)
            response.raise_for_status()
            
            content = response.content
            
            # Determine filename
            filename = request.filename
            if not filename:
                # Try to get from Content-Disposition header
                cd = response.headers.get("content-disposition", "")
                if "filename=" in cd:
                    filename = cd.split("filename=")[1].strip('"')
                else:
                    # Use URL path
                    from urllib.parse import urlparse
                    filename = Path(urlparse(request.url).path).name or "document"
            
            # Save file
            file_id = generate_file_id(filename, content)
            upload_dir = get_upload_dir()
            date_dir = upload_dir / datetime.utcnow().strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            file_ext = Path(filename).suffix or ".html"
            file_path = date_dir / f"{file_id}{file_ext}"
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Fetched URL: {request.url} -> {file_path}")
            
            # Process if requested
            if request.process_immediately and request.collection:
                try:
                    from agentic_assistants.pipelines.nodes import vectorstore_upsert_node
                    
                    text_content = _extract_text_content(file_path)
                    if text_content:
                        vectorstore_upsert_node(
                            documents=[{
                                "content": text_content,
                                "metadata": {
                                    "source_url": request.url,
                                    "source_path": str(file_path),
                                    **request.metadata,
                                },
                            }],
                            config={
                                "collection": request.collection,
                                "project_id": request.project_id,
                                "scope": "project" if request.project_id else "global",
                                "tags": request.tags,
                            },
                        )
                except Exception as e:
                    logger.error(f"Failed to process URL content: {e}")
            
            return FetchResponse(
                success=True,
                source=request.url,
                files_fetched=1,
                total_size_bytes=len(content),
                file_paths=[str(file_path)],
            )
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching URL: {e}")
        return FetchResponse(
            success=False,
            source=request.url,
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=[str(e)],
        )
    except Exception as e:
        logger.error(f"Error fetching URL: {e}")
        return FetchResponse(
            success=False,
            source=request.url,
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=[str(e)],
        )


@router.post("/fetch/github", response_model=FetchResponse)
async def fetch_github(request: FetchGitHubRequest) -> FetchResponse:
    """Fetch files from a GitHub repository."""
    try:
        from agentic_assistants.ingestion.remote_fetcher import GitHubFetcher
        
        fetcher = GitHubFetcher()
        result = await fetcher.fetch(
            repo_url=request.repo_url,
            branch=request.branch,
            paths=request.paths,
            exclude_patterns=request.exclude_patterns,
        )
        
        # Process if requested
        if request.process_immediately and request.collection and result["files"]:
            try:
                from agentic_assistants.pipelines.nodes import vectorstore_upsert_node
                
                documents = []
                for file_path in result["files"]:
                    text_content = _extract_text_content(Path(file_path))
                    if text_content:
                        documents.append({
                            "content": text_content,
                            "metadata": {
                                "source_repo": request.repo_url,
                                "source_branch": request.branch,
                                "source_path": file_path,
                                **request.metadata,
                            },
                        })
                
                if documents:
                    vectorstore_upsert_node(
                        documents=documents,
                        config={
                            "collection": request.collection,
                            "project_id": request.project_id,
                            "scope": "project" if request.project_id else "global",
                            "tags": request.tags,
                        },
                    )
            except Exception as e:
                logger.error(f"Failed to process GitHub content: {e}")
        
        return FetchResponse(
            success=result["success"],
            source=request.repo_url,
            files_fetched=len(result.get("files", [])),
            total_size_bytes=result.get("total_size", 0),
            file_paths=result.get("files", []),
            errors=result.get("errors", []),
        )
        
    except ImportError:
        # Fallback to basic git clone
        return await _fetch_github_basic(request)
    except Exception as e:
        logger.error(f"Error fetching GitHub repo: {e}")
        return FetchResponse(
            success=False,
            source=request.repo_url,
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=[str(e)],
        )


async def _fetch_github_basic(request: FetchGitHubRequest) -> FetchResponse:
    """Basic GitHub fetch using git clone."""
    import subprocess
    
    upload_dir = get_upload_dir()
    repo_name = request.repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest_dir = upload_dir / "github" / repo_name
    
    try:
        # Clone or pull
        if dest_dir.exists():
            subprocess.run(
                ["git", "pull"],
                cwd=dest_dir,
                check=True,
                capture_output=True,
            )
        else:
            dest_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "clone", "--branch", request.branch, "--depth", "1", request.repo_url, str(dest_dir)],
                check=True,
                capture_output=True,
            )
        
        # Collect files
        files = []
        total_size = 0
        
        for file_path in dest_dir.rglob("*"):
            if file_path.is_file():
                # Check exclusions
                skip = False
                for pattern in request.exclude_patterns:
                    if file_path.match(pattern):
                        skip = True
                        break
                
                if not skip:
                    files.append(str(file_path))
                    total_size += file_path.stat().st_size
        
        return FetchResponse(
            success=True,
            source=request.repo_url,
            files_fetched=len(files),
            total_size_bytes=total_size,
            file_paths=files,
        )
        
    except subprocess.CalledProcessError as e:
        return FetchResponse(
            success=False,
            source=request.repo_url,
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=[f"Git error: {e.stderr.decode() if e.stderr else str(e)}"],
        )


@router.post("/fetch/s3", response_model=FetchResponse)
async def fetch_s3(request: FetchS3Request) -> FetchResponse:
    """Fetch files from S3/MinIO."""
    try:
        from agentic_assistants.ingestion.remote_fetcher import S3Fetcher
        
        fetcher = S3Fetcher(endpoint_url=request.endpoint_url)
        result = await fetcher.fetch(
            bucket=request.bucket,
            prefix=request.prefix,
            keys=request.keys,
        )
        
        return FetchResponse(
            success=result["success"],
            source=f"s3://{request.bucket}/{request.prefix}",
            files_fetched=len(result.get("files", [])),
            total_size_bytes=result.get("total_size", 0),
            file_paths=result.get("files", []),
            errors=result.get("errors", []),
        )
        
    except ImportError:
        return FetchResponse(
            success=False,
            source=f"s3://{request.bucket}",
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=["S3 support requires boto3. Install with: pip install boto3"],
        )
    except Exception as e:
        logger.error(f"Error fetching from S3: {e}")
        return FetchResponse(
            success=False,
            source=f"s3://{request.bucket}",
            files_fetched=0,
            total_size_bytes=0,
            file_paths=[],
            errors=[str(e)],
        )


# ============================================================================
# Processing Status
# ============================================================================

@router.get("/status/{job_id}", response_model=ProcessingStatus)
async def get_processing_status(job_id: str) -> ProcessingStatus:
    """Get status of an async processing job."""
    # TODO: Implement job tracking
    return ProcessingStatus(
        job_id=job_id,
        status="unknown",
        progress=0,
        files_processed=0,
        total_files=0,
        errors=["Job tracking not yet implemented"],
    )


# ============================================================================
# Utility Functions
# ============================================================================

def _extract_text_content(file_path: Path) -> Optional[str]:
    """Extract text content from a file."""
    suffix = file_path.suffix.lower()
    
    try:
        # Plain text files
        if suffix in [".txt", ".md", ".rst", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".css", ".xml"]:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        
        # PDF files
        if suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts)
            except ImportError:
                logger.warning("pypdf not installed, cannot extract PDF text")
                return None
        
        # Word documents
        if suffix in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(str(file_path))
                return "\n\n".join([p.text for p in doc.paragraphs if p.text])
            except ImportError:
                logger.warning("python-docx not installed, cannot extract Word text")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None


@router.get("/supported-formats")
async def get_supported_formats() -> dict:
    """Get list of supported file formats."""
    return {
        "text": [".txt", ".md", ".rst"],
        "code": [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h"],
        "documents": [".pdf", ".docx", ".doc"],
        "data": [".json", ".yaml", ".yml", ".xml", ".csv"],
        "web": [".html", ".css"],
    }
