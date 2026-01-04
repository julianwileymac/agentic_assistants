# JupyterLab Configuration for Agentic Assistants
# ================================================
#
# This file configures the JupyterLab server for the development environment.

import os

# Server Configuration
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = int(os.environ.get("JUPYTERLAB_PORT", 3000))
c.ServerApp.open_browser = False

# Disable auth by default inside trusted dev env; override with env vars in production
c.ServerApp.token = os.environ.get("JUPYTERLAB_TOKEN", "")
c.ServerApp.password = os.environ.get("JUPYTERLAB_PASSWORD", "")

# CORS settings for extension communication
c.ServerApp.allow_origin = "*"
c.ServerApp.allow_remote_access = True
c.ServerApp.allow_credentials = True

# WebSocket settings for real-time updates
c.ServerApp.websocket_compression_options = {}

# Set root directory to workspace
c.ServerApp.root_dir = os.environ.get("AGENTIC_WORKSPACE", os.getcwd())

# Notebook settings
c.ServerApp.notebook_dir = os.environ.get("AGENTIC_NOTEBOOK_DIR", "notebooks")

# Content Security Policy - allow loading resources from services
c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://localhost:* http://127.0.0.1:*;"
    }
}

# Extension settings passed to frontend
c.LabApp.extra_labextensions_path = [
    os.path.join(os.path.dirname(__file__), "extensions")
]

# Environment variables for extensions
# These are passed to the frontend JavaScript environment
c.LabServerApp.extra_settings = {
    "MLFLOW_TRACKING_URI": os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"),
    "AGENTIC_BACKEND_URL": os.environ.get("AGENTIC_BACKEND_URL", "http://localhost:8080"),
    "OTEL_EXPORTER_OTLP_ENDPOINT": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
}

# Terminal settings
c.ServerApp.terminals_enabled = True

# Collaborative settings (disable by default for local dev)
c.LabApp.collaborative = False
