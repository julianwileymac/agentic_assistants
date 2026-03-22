#!/usr/bin/env python3
"""
Common Python-based Security Tools Installer

Installs Python-based cybersecurity tools that work across all platforms.
"""

import subprocess
import sys
import platform
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """Python tool metadata."""
    name: str
    package: str
    category: str
    description: str
    requires_python: str = "3.7"


# Python-based security tools
TOOLS = [
    # Network Tools
    Tool(
        name="Scapy",
        package="scapy",
        category="network",
        description="Packet manipulation and network discovery"
    ),
    Tool(
        name="Impacket",
        package="impacket",
        category="exploit",
        description="Network protocols Python library for pentesting"
    ),
    
    # Web Tools
    Tool(
        name="SQLMap",
        package="sqlmap",
        category="web",
        description="Automatic SQL injection tool"
    ),
    Tool(
        name="Wfuzz",
        package="wfuzz",
        category="web",
        description="Web application fuzzer"
    ),
    Tool(
        name="Requests",
        package="requests",
        category="web",
        description="HTTP library for Python"
    ),
    Tool(
        name="BeautifulSoup4",
        package="beautifulsoup4",
        category="web",
        description="HTML/XML parsing library"
    ),
    
    # Exploitation
    Tool(
        name="Pwntools",
        package="pwntools",
        category="exploit",
        description="CTF framework and exploit development library",
        requires_python="3.6"
    ),
    Tool(
        name="ROPGadget",
        package="ROPGadget",
        category="exploit",
        description="ROP gadget finder and auto-roper"
    ),
    
    # Forensics
    Tool(
        name="Volatility3",
        package="volatility3",
        category="forensics",
        description="Memory forensics framework"
    ),
    
    # Password Cracking
    Tool(
        name="Passlib",
        package="passlib",
        category="password",
        description="Password hashing library"
    ),
    
    # Utilities
    Tool(
        name="Paramiko",
        package="paramiko",
        category="network",
        description="SSH2 protocol library"
    ),
    Tool(
        name="PyCrypto",
        package="pycryptodome",
        category="crypto",
        description="Cryptographic library"
    ),
    Tool(
        name="Python-Nmap",
        package="python-nmap",
        category="network",
        description="Python wrapper for Nmap"
    ),
]


class Color:
    """ANSI color codes."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text: str, color: str = Color.RESET, bold: bool = False):
    """Print colored text."""
    if bold:
        print(f"{Color.BOLD}{color}{text}{Color.RESET}")
    else:
        print(f"{color}{text}{Color.RESET}")


def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print_colored("Error: Python 3.6 or higher is required", Color.RED, bold=True)
        print_colored(f"Current version: {sys.version}", Color.YELLOW)
        sys.exit(1)
    
    print_colored(f"✓ Python {version.major}.{version.minor}.{version.micro}", Color.GREEN)


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True
        )
        print_colored("✓ pip is available", Color.GREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("✗ pip is not available", Color.RED, bold=True)
        print_colored("Please install pip: https://pip.pypa.io/en/stable/installation/", Color.YELLOW)
        return False


def is_tool_installed(package: str) -> bool:
    """Check if a Python package is installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def install_tool(tool: Tool) -> bool:
    """Install a Python tool via pip."""
    print(f"Installing {tool.name}... ", end="", flush=True)
    
    # Check if already installed
    if is_tool_installed(tool.package):
        print_colored("already installed", Color.YELLOW)
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", tool.package],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_colored("✓ success", Color.GREEN)
            return True
        else:
            print_colored("✗ failed", Color.RED)
            print_colored(f"Error: {result.stderr}", Color.RED)
            return False
    
    except subprocess.TimeoutExpired:
        print_colored("✗ timeout", Color.RED)
        return False
    except Exception as e:
        print_colored(f"✗ error: {e}", Color.RED)
        return False


def upgrade_pip():
    """Upgrade pip to latest version."""
    print("Upgrading pip... ", end="", flush=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            check=True,
            timeout=60
        )
        print_colored("✓ success", Color.GREEN)
        return True
    except Exception as e:
        print_colored(f"! warning: {e}", Color.YELLOW)
        return False


def list_tools(category: Optional[str] = None):
    """List available tools."""
    print_colored("\n=== Available Python Security Tools ===", Color.BLUE, bold=True)
    print()
    
    categories = set(tool.category for tool in TOOLS)
    
    for cat in sorted(categories):
        if category and cat != category:
            continue
        
        print_colored(f"Category: {cat.upper()}", Color.CYAN, bold=True)
        
        for tool in TOOLS:
            if tool.category == cat:
                installed = is_tool_installed(tool.package)
                status = "✓" if installed else "✗"
                color = Color.GREEN if installed else Color.YELLOW
                
                print_colored(
                    f"  {status} {tool.name:20s} - {tool.description}",
                    color
                )
        print()


def install_category(category: str):
    """Install all tools in a category."""
    tools_to_install = [t for t in TOOLS if t.category == category]
    
    if not tools_to_install:
        print_colored(f"No tools found in category: {category}", Color.YELLOW)
        return
    
    print_colored(f"\n=== Installing {category.upper()} tools ===", Color.BLUE, bold=True)
    print()
    
    success_count = 0
    for tool in tools_to_install:
        if install_tool(tool):
            success_count += 1
    
    print()
    print_colored(
        f"Installed {success_count}/{len(tools_to_install)} tools",
        Color.GREEN if success_count == len(tools_to_install) else Color.YELLOW,
        bold=True
    )


def install_all():
    """Install all tools."""
    print_colored("\n=== Installing ALL Python Security Tools ===", Color.BLUE, bold=True)
    print()
    
    success_count = 0
    for tool in TOOLS:
        if install_tool(tool):
            success_count += 1
    
    print()
    print_colored(
        f"Installed {success_count}/{len(TOOLS)} tools",
        Color.GREEN if success_count == len(TOOLS) else Color.YELLOW,
        bold=True
    )


def main():
    """Main installer function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Install Python-based cybersecurity tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Categories:
  network    - Network scanning and packet manipulation
  web        - Web application testing
  exploit    - Exploitation and CTF tools
  forensics  - Digital forensics
  password   - Password cracking utilities
  crypto     - Cryptography tools

Examples:
  python install_common.py --list
  python install_common.py --category network
  python install_common.py --all
  python install_common.py --tool scapy
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tools and their installation status"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Install all tools in a specific category"
    )
    parser.add_argument(
        "--tool",
        type=str,
        help="Install a specific tool by package name"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install all available tools"
    )
    parser.add_argument(
        "--upgrade-pip",
        action="store_true",
        help="Upgrade pip before installing"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check system compatibility"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_colored("\n" + "="*50, Color.BLUE)
    print_colored("Python Security Tools Installer", Color.BLUE, bold=True)
    print_colored("="*50 + "\n", Color.BLUE)
    
    # Check Python version
    print("Checking system compatibility...")
    check_python_version()
    
    if not check_pip():
        sys.exit(1)
    
    print_colored(f"✓ Platform: {platform.system()} {platform.machine()}", Color.GREEN)
    print()
    
    # Check only
    if args.check:
        print_colored("System check complete!", Color.GREEN, bold=True)
        sys.exit(0)
    
    # Upgrade pip
    if args.upgrade_pip:
        upgrade_pip()
        print()
    
    # List tools
    if args.list:
        list_tools()
        sys.exit(0)
    
    # Install specific tool
    if args.tool:
        tool_obj = next((t for t in TOOLS if t.package == args.tool), None)
        if tool_obj:
            install_tool(tool_obj)
        else:
            print_colored(f"Tool not found: {args.tool}", Color.RED)
            print_colored("Use --list to see available tools", Color.YELLOW)
        sys.exit(0)
    
    # Install by category
    if args.category:
        install_category(args.category)
        sys.exit(0)
    
    # Install all
    if args.all:
        if args.upgrade_pip:
            upgrade_pip()
        install_all()
        sys.exit(0)
    
    # No arguments - show help
    parser.print_help()
    print()
    print_colored("Tip: Use --list to see available tools", Color.CYAN)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\nInstallation cancelled by user", Color.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\nUnexpected error: {e}", Color.RED, bold=True)
        sys.exit(1)
