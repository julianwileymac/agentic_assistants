"""
FastAPI endpoints for Cybersecurity Hub.

Provides REST API for cybersecurity operations.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/cybersec", tags=["cybersecurity"])


# Request/Response Models
class ToolInstallRequest(BaseModel):
    """Tool installation request."""
    tool_name: str
    category: Optional[str] = None


class ToolExecuteRequest(BaseModel):
    """Tool execution request."""
    tool: str
    target: str
    options: List[str] = Field(default_factory=list)
    stealth: bool = False
    timeout: Optional[int] = None


class ScanRequest(BaseModel):
    """Scan request."""
    target: str
    scan_type: str = "standard"  # quick, standard, comprehensive
    stealth: bool = False
    save_results: bool = True


class TargetAuthorizeRequest(BaseModel):
    """Target authorization request."""
    identifier: str
    authorization_token: str
    authorized_by: str
    description: Optional[str] = None
    scope: List[str] = Field(default_factory=list)


class LogAnalysisRequest(BaseModel):
    """Log analysis request."""
    source: str
    detect_anomalies: bool = True
    time_range: Optional[tuple] = None


class WorkflowCreateRequest(BaseModel):
    """Workflow creation request."""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    schedule: Optional[str] = None


class ReportGenerateRequest(BaseModel):
    """Report generation request."""
    scan_ids: Optional[List[str]] = None
    format: str = "html"  # html, pdf, json, markdown


# Dependency to get cybersec hub instance
def get_cybersec_hub():
    """Get or create CybersecHub instance."""
    # In production, this would be a singleton or managed by the application
    # For now, we'll import and create it
    try:
        from examples.cybersec_hub import CybersecHub
        return CybersecHub()
    except Exception as e:
        logger.error(f"Failed to initialize CybersecHub: {e}")
        raise HTTPException(status_code=500, detail="Cybersec Hub not available")


# Tool Management Endpoints
@router.get("/tools")
async def list_tools(
    category: Optional[str] = None,
    installed_only: bool = False,
    hub = Depends(get_cybersec_hub)
):
    """List available security tools."""
    try:
        tools = hub.list_tools(category=category)
        
        if installed_only:
            tools = [t for t in tools if t.status.value == "installed"]
        
        return {
            "success": True,
            "count": len(tools),
            "tools": [
                {
                    "name": t.name,
                    "category": t.category,
                    "description": t.description,
                    "status": t.status.value,
                    "capabilities": t.capabilities,
                    "os_support": t.os_support
                }
                for t in tools
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/install")
async def install_tool(
    request: ToolInstallRequest,
    background_tasks: BackgroundTasks,
    hub = Depends(get_cybersec_hub)
):
    """Install a security tool."""
    try:
        # Run installation in background
        success = hub.install_tool(request.tool_name)
        
        return {
            "success": success,
            "tool": request.tool_name,
            "message": "Installation initiated" if success else "Installation failed"
        }
    except Exception as e:
        logger.error(f"Tool installation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/{tool_id}/execute")
async def execute_tool(
    tool_id: str,
    request: ToolExecuteRequest,
    hub = Depends(get_cybersec_hub)
):
    """Execute a security tool."""
    try:
        result = hub.scan_target(
            target=request.target,
            tool=request.tool,
            options=request.options,
            stealth=request.stealth
        )
        
        return {
            "success": result.status == "completed",
            "scan_id": result.scan_id,
            "findings": len(result.findings),
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Operations Endpoints
@router.post("/operations/scan")
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    hub = Depends(get_cybersec_hub)
):
    """Start a security scan."""
    try:
        # Get red team agent
        red_team = hub.get_agent("red_team")
        
        # Start scan
        operation = red_team.scan_target(
            target=request.target,
            scan_type=request.scan_type,
            stealth=request.stealth,
            save_results=request.save_results
        )
        
        return {
            "success": operation.status == "completed",
            "operation_id": operation.operation_id,
            "target": operation.target,
            "findings": len(operation.findings),
            "status": operation.status
        }
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations/{operation_id}")
async def get_operation(
    operation_id: str,
    hub = Depends(get_cybersec_hub)
):
    """Get operation status and results."""
    try:
        red_team = hub.get_agent("red_team")
        
        if operation_id not in red_team.operations:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        operation = red_team.operations[operation_id]
        
        return {
            "operation_id": operation.operation_id,
            "target": operation.target,
            "type": operation.operation_type,
            "status": operation.status,
            "start_time": operation.start_time,
            "end_time": operation.end_time,
            "findings": operation.findings
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Target Management Endpoints
@router.post("/network/targets")
async def authorize_target(
    request: TargetAuthorizeRequest,
    hub = Depends(get_cybersec_hub)
):
    """Authorize a target for testing."""
    try:
        target_manager = hub.network_manager["targets"]
        
        target = target_manager.authorize_target(
            identifier=request.identifier,
            authorization_token=request.authorization_token,
            authorized_by=request.authorized_by,
            description=request.description,
            scope=request.scope if request.scope else None
        )
        
        return {
            "success": True,
            "target_id": target.target_id,
            "identifier": target.identifier,
            "authorized_at": target.authorized_at
        }
    except Exception as e:
        logger.error(f"Target authorization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/targets")
async def list_targets(
    active_only: bool = True,
    hub = Depends(get_cybersec_hub)
):
    """List authorized targets."""
    try:
        target_manager = hub.network_manager["targets"]
        targets = target_manager.list_targets(active_only=active_only)
        
        return {
            "success": True,
            "count": len(targets),
            "targets": [
                {
                    "target_id": t.target_id,
                    "identifier": t.identifier,
                    "description": t.description,
                    "authorized_by": t.authorized_by,
                    "authorized_at": t.authorized_at,
                    "expires_at": t.expires_at
                }
                for t in targets
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list targets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# VPN Management Endpoints
@router.get("/network/vpn/profiles")
async def list_vpn_profiles(
    country: Optional[str] = None,
    hub = Depends(get_cybersec_hub)
):
    """List available VPN profiles."""
    try:
        vpn_manager = hub.network_manager["vpn"]
        profiles = vpn_manager.list_profiles(country=country)
        
        return {
            "success": True,
            "count": len(profiles),
            "profiles": [
                {
                    "profile_id": p.profile_id,
                    "name": p.name,
                    "country": p.country,
                    "protocol": p.protocol
                }
                for p in profiles
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list VPN profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/network/vpn/connect")
async def connect_vpn(
    profile_id: Optional[str] = None,
    hub = Depends(get_cybersec_hub)
):
    """Connect to VPN."""
    try:
        success = hub.connect_vpn(profile=profile_id)
        
        return {
            "success": success,
            "message": "Connected to VPN" if success else "Connection failed"
        }
    except Exception as e:
        logger.error(f"VPN connection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/network/vpn/disconnect")
async def disconnect_vpn(hub = Depends(get_cybersec_hub)):
    """Disconnect from VPN."""
    try:
        success = hub.disconnect_vpn()
        
        return {
            "success": success,
            "message": "Disconnected from VPN" if success else "Disconnection failed"
        }
    except Exception as e:
        logger.error(f"VPN disconnection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analysis Endpoints
@router.post("/analysis/logs")
async def analyze_logs(
    request: LogAnalysisRequest,
    hub = Depends(get_cybersec_hub)
):
    """Analyze security logs."""
    try:
        results = hub.analyze_logs(
            source=request.source,
            detect_anomalies=request.detect_anomalies
        )
        
        return {
            "success": True,
            "source": request.source,
            "total_events": results.get("total_events", 0),
            "anomalies": len(results.get("anomalies", [])),
            "threats": len(results.get("threats", [])),
            "results": results
        }
    except Exception as e:
        logger.error(f"Log analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/anomalies")
async def get_anomalies(
    severity: Optional[str] = None,
    hub = Depends(get_cybersec_hub)
):
    """Get detected anomalies."""
    try:
        blue_team = hub.get_agent("blue_team")
        anomalies = blue_team.detect_anomalies(threshold=0.8)
        
        if severity:
            anomalies = [a for a in anomalies if a.get("severity") == severity]
        
        return {
            "success": True,
            "count": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Report Endpoints
@router.post("/reports/generate")
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    hub = Depends(get_cybersec_hub)
):
    """Generate security assessment report."""
    try:
        report_path = hub.generate_report(
            scan_ids=request.scan_ids,
            format=request.format
        )
        
        return {
            "success": True,
            "report_path": report_path,
            "format": request.format,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def list_reports(hub = Depends(get_cybersec_hub)):
    """List generated reports."""
    try:
        # In production, would scan reports directory
        reports_dir = hub.reports_dir
        
        reports = []
        if reports_dir.exists():
            for report_file in reports_dir.glob("security_report_*"):
                reports.append({
                    "filename": report_file.name,
                    "path": str(report_file),
                    "size": report_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(report_file.stat().st_ctime).isoformat()
                })
        
        return {
            "success": True,
            "count": len(reports),
            "reports": reports
        }
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Assistant Endpoints
@router.post("/assistant/chat")
async def chat_with_assistant(
    query: str,
    hub = Depends(get_cybersec_hub)
):
    """Chat with security assistant."""
    try:
        assistant = hub.get_assistant()
        response = assistant.chat(query)
        
        return {
            "success": True,
            "query": response.query,
            "response": response.response,
            "sources": response.sources,
            "confidence": response.confidence
        }
    except Exception as e:
        logger.error(f"Assistant chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assistant/recommend-tool")
async def recommend_tool(
    task: str,
    hub = Depends(get_cybersec_hub)
):
    """Get tool recommendations."""
    try:
        assistant = hub.get_assistant()
        recommendations = assistant.recommend_tool(task)
        
        return {
            "success": True,
            "task": task,
            "recommendations": recommendations["recommendations"],
            "advice": recommendations["advice"]
        }
    except Exception as e:
        logger.error(f"Tool recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "cybersec-hub",
        "timestamp": datetime.now().isoformat()
    }
