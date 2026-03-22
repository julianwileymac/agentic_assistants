# Cybersecurity Hub

A comprehensive cybersecurity tooling, learning, and exploration hub built on the Agentic Assistants framework. This project provides an integrated environment for red team operations, blue team monitoring, vulnerability assessment, and security learning—all powered by AI/ML capabilities.

## Overview

The Cybersecurity Hub is designed to support:

- **Red Team Operations**: Automated reconnaissance, vulnerability scanning, and exploitation workflows
- **Blue Team Monitoring**: Log analysis, intrusion detection, and incident response
- **Learning & Exploration**: Interactive tutorials, technique walkthroughs, and AI-assisted guidance
- **International Testing**: VPN/proxy integration for exploring security resources across countries
- **AI/ML Integration**: Anomaly detection, vulnerability prediction, and intelligent security assistance

## Features

### Tool Management
- Automated installation of common cybersecurity tools
- Support for Linux and Windows operating systems
- Containerized tool execution for isolation
- Python wrappers for programmatic access
- Tool documentation and usage guidance

### Specialized Agents
- **Red Team Agent**: Orchestrates offensive security operations
- **Blue Team Agent**: Monitors and defends against threats
- **Vulnerability Scanner Agent**: Automated scanning and prioritization
- **Log Analyzer Agent**: AI-powered log analysis and correlation

### Interactive Dashboard
- Real-time operations console
- Visual workflow builder for automation
- Log analysis and anomaly detection viewer
- Report generation and export
- Learning hub with tutorials and AI assistant

### AI/ML Capabilities
- Log anomaly detection using unsupervised learning
- Vulnerability prediction and prioritization
- RAG-based security knowledge base
- Tool recommendation engine
- Natural language interface for security operations

### Network & Deployment
- VPN/proxy integration for international testing
- Target network management
- Docker Compose deployment
- Kubernetes orchestration
- Isolated test environments

## Quick Start

### Prerequisites

- Python 3.10 or 3.11
- Poetry for dependency management
- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (optional, for production deployment)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd examples/cybersec-hub
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Initialize configuration:**
   ```bash
   # Copy and customize the configuration
   cp config.yaml config.local.yaml
   # Edit config.local.yaml with your settings
   ```

4. **Install security tools:**
   
   For Linux:
   ```bash
   bash scripts/install_linux.sh
   ```
   
   For Windows (PowerShell as Administrator):
   ```powershell
   .\scripts\install_windows.ps1
   ```

5. **Start the hub:**
   ```bash
   # Using Docker Compose
   docker-compose -f docker/docker-compose.yml up -d
   
   # Or run directly
   python -m cybersec_hub
   ```

6. **Access the dashboard:**
   - Dashboard: http://localhost:3002
   - API: http://localhost:8081
   - MLFlow: http://localhost:5000

## Configuration

The hub is configured via `config.yaml`. Key configuration sections:

### Cybersec Mode
```yaml
cybersec:
  mode: "full"  # Options: full, red-only, blue-only, learning
  red_team:
    enabled: true
    auto_exploit: false  # Require manual confirmation for exploitation
    stealth_mode: true
  blue_team:
    enabled: true
    monitoring_interval: 60
```

### Tool Configuration
```yaml
cybersec:
  tools:
    install_on_startup: false
    auto_update: true
    containerized_execution: true
```

### Network & VPN
```yaml
cybersec:
  network:
    vpn_enabled: true
    default_vpn_profile: "us-east-1"
    international_mode: true
```

### AI/ML Settings
```yaml
cybersec:
  ml:
    anomaly_detection:
      enabled: true
      model: "isolation-forest"
    assistant:
      enabled: true
      model: "llama3:8b"
```

## Architecture

```
CybersecHub (Main Orchestrator)
├── Tool Manager (Installation, execution, wrapping)
├── Agent System
│   ├── Red Team Agent
│   ├── Blue Team Agent
│   ├── Vulnerability Scanner
│   └── Log Analyzer
├── ML Engine
│   ├── Anomaly Detection
│   ├── Vulnerability Prediction
│   └── Security Assistant (RAG)
├── Automation Framework
│   ├── Scanner Workflows
│   ├── Exploit Chains
│   └── Monitoring Pipelines
├── Network Manager
│   ├── VPN/Proxy Integration
│   ├── Target Management
│   └── International Resources
└── Knowledge Base (Vector DB)
    ├── Tool Documentation
    ├── Exploit Techniques
    ├── Security Logs
    └── CVE Database
```

## Usage Examples

### Red Team Operations

```python
from cybersec_hub import CybersecHub

hub = CybersecHub()

# Initialize red team agent
red_team = hub.get_agent("red_team")

# Run automated reconnaissance
results = red_team.scan_target(
    target="192.168.1.0/24",
    scan_type="comprehensive",
    stealth=True
)

# Analyze vulnerabilities
vulns = red_team.analyze_vulnerabilities(results)

# Generate report
report = red_team.generate_report(vulns)
```

### Blue Team Monitoring

```python
from cybersec_hub import CybersecHub

hub = CybersecHub()

# Initialize blue team agent
blue_team = hub.get_agent("blue_team")

# Start continuous monitoring
blue_team.start_monitoring(
    sources=["syslog", "auth.log", "firewall.log"],
    alert_threshold=0.8
)

# Analyze logs for anomalies
anomalies = blue_team.detect_anomalies()

# Trigger automated response
for anomaly in anomalies:
    if anomaly.severity == "critical":
        blue_team.respond_to_threat(anomaly)
```

### Interactive Scripting

```python
from cybersec_hub import CybersecHub
from cybersec_hub.tools import ToolManager

hub = CybersecHub()
tools = ToolManager(hub)

# Execute nmap scan
nmap_results = tools.execute(
    tool="nmap",
    target="scanme.nmap.org",
    options=["-sV", "-p-"]
)

# Parse and store results in knowledge base
parsed = tools.parse_output("nmap", nmap_results)
hub.knowledge_base.store(parsed, collection="scan-results")

# Query AI assistant for recommendations
assistant = hub.get_assistant()
advice = assistant.chat(
    f"Based on these nmap results, what should I investigate next? {parsed}"
)
print(advice)
```

### Automation Workflows

```python
from cybersec_hub import CybersecHub
from cybersec_hub.automation import ScannerWorkflow

hub = CybersecHub()

# Define automated scanning workflow
workflow = ScannerWorkflow()
workflow.add_step("discovery", tool="nmap", options="-sn")
workflow.add_step("port_scan", tool="nmap", options="-p-", depends_on="discovery")
workflow.add_step("vuln_scan", tool="nikto", depends_on="port_scan")
workflow.add_step("analyze", agent="vulnerability_scanner", depends_on="vuln_scan")

# Execute workflow
results = workflow.execute(target="192.168.1.0/24")

# Schedule for recurring execution
workflow.schedule(cron="0 2 * * *")  # Daily at 2 AM
```

## Tool Categories

### Network Tools
- nmap, masscan, zmap - Network scanning
- netcat, tcpdump - Network utilities

### Web Application Testing
- OWASP ZAP, Burp Suite - Web proxy and scanner
- nikto, dirb, sqlmap, wfuzz - Specialized testing

### Exploitation
- Metasploit Framework - Exploitation platform
- PowerShell Empire - Post-exploitation

### Forensics & Analysis
- Wireshark - Network protocol analyzer
- Volatility - Memory forensics

### Password Attacks
- Hashcat, John the Ripper - Password cracking
- Hydra, Medusa - Network authentication attacks

### Wireless Security
- Aircrack-ng - Wireless security testing
- Kismet - Wireless detection

## Dashboard Pages

- **Overview**: System status, active operations, recent findings
- **Tools**: Installation, configuration, execution interface
- **Operations**: Red team and blue team consoles
- **Automation**: Visual workflow builder and scheduler
- **Logs & Analysis**: Log viewer with anomaly detection
- **Reports**: Generated reports and vulnerability dashboards
- **Learning**: Interactive tutorials and AI assistant
- **Network**: VPN/proxy management and target configuration

## Safety & Legal Considerations

### Important Warnings

⚠️ **This tool is for educational and authorized security testing only.**

- Always obtain explicit written authorization before testing any systems
- Unauthorized access to computer systems is illegal
- Many security tools can cause disruption—use responsibly
- Adhere to all applicable laws and regulations

### Built-in Safeguards

1. **Authorization Layer**: All operations require confirmation
2. **Target Whitelisting**: Enforce approved target lists
3. **Audit Logging**: Complete operation history
4. **Isolation**: Tools run in containers
5. **Manual Exploit Approval**: Auto-exploitation disabled by default

### Ethical Guidelines

- Follow the principle of responsible disclosure
- Respect privacy and data protection laws
- Only test systems you own or have permission to test
- Document and report findings appropriately
- Use knowledge to improve security, not exploit vulnerabilities

## Deployment

### Docker Compose (Local Development)

```bash
cd docker
docker-compose up -d
```

Services:
- Cybersec Hub API: Port 8081
- Dashboard: Port 3002
- VPN Gateway: For international testing

### Kubernetes (Production)

```bash
cd k8s
kubectl apply -k overlays/production
```

Features:
- Scalable agent execution
- Persistent storage for data and tools
- Scheduled vulnerability scans via CronJobs
- Network isolation and security policies

## API Endpoints

### Tool Management
- `GET /api/v1/cybersec/tools` - List installed tools
- `POST /api/v1/cybersec/tools/install` - Install tool
- `POST /api/v1/cybersec/tools/{tool_id}/execute` - Execute tool

### Operations
- `POST /api/v1/cybersec/operations/scan` - Start scan
- `POST /api/v1/cybersec/operations/exploit` - Execute exploit
- `GET /api/v1/cybersec/operations/{id}` - Get operation status

### Automation
- `GET /api/v1/cybersec/automation/workflows` - List workflows
- `POST /api/v1/cybersec/automation/workflows` - Create workflow
- `POST /api/v1/cybersec/automation/workflows/{id}/execute` - Run workflow

### Analysis
- `POST /api/v1/cybersec/analysis/logs` - Analyze logs
- `GET /api/v1/cybersec/analysis/anomalies` - Get anomalies

### Reports
- `GET /api/v1/cybersec/reports` - List reports
- `POST /api/v1/cybersec/reports/generate` - Generate report
- `GET /api/v1/cybersec/reports/{id}/export` - Export report

## Knowledge Base

The hub maintains a vector database with:

- **Tool Documentation**: Usage guides and examples
- **Exploit Techniques**: MITRE ATT&CK mapped techniques
- **Security Logs**: Historical logs for training ML models
- **CVE Database**: Vulnerability information and patches
- **Reports**: Past assessment results and findings

## Learning Resources

### Interactive Tutorials
- Tool-specific walkthroughs
- MITRE ATT&CK technique explanations
- Common vulnerability patterns
- Exploitation methodologies

### Practice Environments
- DVWA (Damn Vulnerable Web Application)
- Metasploitable virtual machines
- HackTheBox integration
- Custom challenge environments

### AI Assistant
- Real-time security guidance
- Tool recommendations
- Exploit suggestions
- Defensive strategies

## Troubleshooting

### Tools Not Installing
```bash
# Check OS compatibility
python scripts/install_common.py --check

# Install manually
sudo apt-get update
sudo apt-get install <tool-name>
```

### VPN Connection Issues
```bash
# Check VPN configuration
cat network/vpn-configs/your-profile.ovpn

# Test connection
python -m cybersec_hub.network.vpn_manager --test
```

### Agent Not Responding
```bash
# Check logs
tail -f data/logs/cybersec-hub.log

# Restart agent
docker-compose restart cybersec-hub
```

### Dashboard Not Loading
```bash
# Check API connectivity
curl http://localhost:8081/api/v1/health

# Check browser console for errors
# Ensure all services are running
docker-compose ps
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional tool wrappers
- New agent capabilities
- ML model enhancements
- Dashboard features
- Documentation and tutorials

## License

This project is licensed under the same terms as the Agentic Assistants framework.

## Acknowledgments

- MITRE ATT&CK framework
- OWASP community
- Open-source security tool developers
- Agentic Assistants framework team

## Resources

- [MITRE ATT&CK](https://attack.mitre.org/)
- [OWASP](https://owasp.org/)
- [CVE Database](https://cve.mitre.org/)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. The authors and contributors are not responsible for any misuse or damage caused by this software. Users are solely responsible for ensuring their activities comply with applicable laws and regulations.
