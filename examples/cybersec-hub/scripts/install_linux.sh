#!/bin/bash

###############################################################################
# Cybersecurity Hub - Linux Tool Installation Script
#
# Installs common cybersecurity tools on Linux systems.
# Supports: Ubuntu/Debian (apt), RHEL/CentOS (yum), Arch (pacman)
#
# Usage: sudo bash install_linux.sh [category]
#   category: network, web, exploit, forensics, password, wireless, all (default)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
CATEGORY="${1:-all}"
LOG_FILE="./install_$(date +%Y%m%d_%H%M%S).log"

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}Cybersecurity Hub Tool Installer${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Detect package manager
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)

if [ "$PKG_MANAGER" == "unknown" ]; then
    echo -e "${RED}Error: No supported package manager found${NC}"
    exit 1
fi

echo -e "${GREEN}Detected package manager: ${PKG_MANAGER}${NC}"
echo -e "${BLUE}Installation category: ${CATEGORY}${NC}"
echo -e "${BLUE}Log file: ${LOG_FILE}${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Not running as root. You may need to enter your password.${NC}"
    echo ""
fi

# Update package lists
echo -e "${BLUE}Updating package lists...${NC}"
case $PKG_MANAGER in
    apt)
        sudo apt-get update >> "$LOG_FILE" 2>&1
        ;;
    yum)
        sudo yum check-update >> "$LOG_FILE" 2>&1 || true
        ;;
    pacman)
        sudo pacman -Sy >> "$LOG_FILE" 2>&1
        ;;
esac
echo -e "${GREEN}✓ Package lists updated${NC}"
echo ""

# Install function
install_tool() {
    local tool_name=$1
    local apt_pkg=$2
    local yum_pkg=$3
    local pacman_pkg=$4
    
    echo -n "Installing ${tool_name}... "
    
    # Check if already installed
    if command -v "${tool_name}" &> /dev/null; then
        echo -e "${YELLOW}already installed${NC}"
        return 0
    fi
    
    case $PKG_MANAGER in
        apt)
            if sudo apt-get install -y "${apt_pkg}" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓ success${NC}"
            else
                echo -e "${RED}✗ failed${NC}"
                return 1
            fi
            ;;
        yum)
            if sudo yum install -y "${yum_pkg:-$apt_pkg}" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓ success${NC}"
            else
                echo -e "${RED}✗ failed${NC}"
                return 1
            fi
            ;;
        pacman)
            if sudo pacman -S --noconfirm "${pacman_pkg:-$apt_pkg}" >> "$LOG_FILE" 2>&1; then
                echo -e "${GREEN}✓ success${NC}"
            else
                echo -e "${RED}✗ failed${NC}"
                return 1
            fi
            ;;
    esac
}

# Install Python tool via pip
install_pip_tool() {
    local tool_name=$1
    local pip_package=$2
    
    echo -n "Installing ${tool_name} (via pip)... "
    
    if python3 -m pip show "${pip_package}" &> /dev/null; then
        echo -e "${YELLOW}already installed${NC}"
        return 0
    fi
    
    if python3 -m pip install "${pip_package}" >> "$LOG_FILE" 2>&1; then
        echo -e "${GREEN}✓ success${NC}"
    else
        echo -e "${RED}✗ failed${NC}"
        return 1
    fi
}

# Network Tools
install_network_tools() {
    echo -e "${BLUE}=== Installing Network Tools ===${NC}"
    install_tool "nmap" "nmap" "nmap" "nmap"
    install_tool "masscan" "masscan" "masscan" ""
    install_tool "netcat" "netcat" "nc" "netcat"
    install_tool "tcpdump" "tcpdump" "tcpdump" "tcpdump"
    
    # Python-based
    install_pip_tool "scapy" "scapy"
    
    echo ""
}

# Web Application Tools
install_web_tools() {
    echo -e "${BLUE}=== Installing Web Application Tools ===${NC}"
    install_tool "nikto" "nikto" "nikto" "nikto"
    install_tool "dirb" "dirb" "dirb" ""
    install_tool "sqlmap" "sqlmap" "sqlmap" "sqlmap"
    install_pip_tool "wfuzz" "wfuzz"
    
    # OWASP ZAP (via snap if available)
    if command -v snap &> /dev/null; then
        echo -n "Installing OWASP ZAP (via snap)... "
        if sudo snap install zaproxy --classic >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}✓ success${NC}"
        else
            echo -e "${YELLOW}! skipped (snap not available or failed)${NC}"
        fi
    fi
    
    echo ""
}

# Exploitation Tools
install_exploit_tools() {
    echo -e "${BLUE}=== Installing Exploitation Tools ===${NC}"
    
    # Metasploit Framework
    echo -n "Installing Metasploit Framework... "
    if command -v msfconsole &> /dev/null; then
        echo -e "${YELLOW}already installed${NC}"
    else
        echo "Downloading installer..."
        curl -s https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall
        chmod 755 /tmp/msfinstall
        if sudo /tmp/msfinstall >> "$LOG_FILE" 2>&1; then
            echo -e "${GREEN}✓ success${NC}"
        else
            echo -e "${RED}✗ failed (see log for details)${NC}"
        fi
    fi
    
    # Python-based tools
    install_pip_tool "impacket" "impacket"
    install_pip_tool "pwntools" "pwntools"
    
    echo ""
}

# Forensics Tools
install_forensics_tools() {
    echo -e "${BLUE}=== Installing Forensics Tools ===${NC}"
    install_tool "tshark" "tshark" "wireshark" "wireshark-cli"
    install_tool "wireshark" "wireshark" "wireshark" "wireshark-qt"
    
    # Volatility
    install_pip_tool "volatility3" "volatility3"
    
    echo ""
}

# Password Tools
install_password_tools() {
    echo -e "${BLUE}=== Installing Password Attack Tools ===${NC}"
    install_tool "john" "john" "john" "john"
    install_tool "hashcat" "hashcat" "hashcat" "hashcat"
    install_tool "hydra" "hydra" "hydra" "hydra"
    install_tool "medusa" "medusa" "medusa" "medusa"
    
    echo ""
}

# Wireless Tools
install_wireless_tools() {
    echo -e "${BLUE}=== Installing Wireless Security Tools ===${NC}"
    install_tool "aircrack-ng" "aircrack-ng" "aircrack-ng" "aircrack-ng"
    install_tool "kismet" "kismet" "kismet" "kismet"
    
    echo ""
}

# Docker setup
setup_docker() {
    echo -e "${BLUE}=== Setting up Docker for tool containers ===${NC}"
    
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker already installed${NC}"
    else
        echo "Installing Docker..."
        case $PKG_MANAGER in
            apt)
                sudo apt-get install -y docker.io >> "$LOG_FILE" 2>&1
                ;;
            yum)
                sudo yum install -y docker >> "$LOG_FILE" 2>&1
                ;;
            pacman)
                sudo pacman -S --noconfirm docker >> "$LOG_FILE" 2>&1
                ;;
        esac
        
        sudo systemctl enable docker
        sudo systemctl start docker
        echo -e "${GREEN}✓ Docker installed and started${NC}"
    fi
    
    # Add current user to docker group
    if ! groups | grep -q docker; then
        echo "Adding user to docker group..."
        sudo usermod -aG docker "$USER"
        echo -e "${YELLOW}! You need to log out and back in for docker group to take effect${NC}"
    fi
    
    echo ""
}

# Main installation
case $CATEGORY in
    network)
        install_network_tools
        ;;
    web)
        install_web_tools
        ;;
    exploit)
        install_exploit_tools
        ;;
    forensics)
        install_forensics_tools
        ;;
    password)
        install_password_tools
        ;;
    wireless)
        install_wireless_tools
        ;;
    all)
        install_network_tools
        install_web_tools
        install_exploit_tools
        install_forensics_tools
        install_password_tools
        install_wireless_tools
        ;;
    *)
        echo -e "${RED}Error: Unknown category: $CATEGORY${NC}"
        echo "Valid categories: network, web, exploit, forensics, password, wireless, all"
        exit 1
        ;;
esac

# Setup Docker
echo -e "${BLUE}Would you like to set up Docker for containerized tool execution? [y/N]${NC}"
read -r -n 1 response
echo
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    setup_docker
fi

echo ""
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${BLUE}Log file: ${LOG_FILE}${NC}"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "1. Some tools may require additional configuration"
echo "2. Ensure you have proper authorization before using these tools"
echo "3. See documentation for tool-specific usage instructions"
echo "4. If you added yourself to the docker group, log out and back in"
echo ""
echo -e "${YELLOW}Legal Warning:${NC}"
echo "These tools are for educational and authorized security testing only."
echo "Unauthorized access to computer systems is illegal."
echo ""
