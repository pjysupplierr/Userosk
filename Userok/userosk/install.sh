#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  ULTIMATE SECURITY HUB - AUTO INSTALLER v5.2              ║
# ║  Installs ALL dependencies, tools, and Python packages     ║
# ║  Run: chmod +x install.sh && sudo ./install.sh            ║
# ╚════════════════════════════════════════════════════════════╝
set -e

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${GREEN}${BOLD}████████╗███████╗██████╗ ███╗   ███╗${RESET}"
echo -e "${GREEN}${BOLD}╚══██╔══╝██╔════╝██╔══██╗████╗ ████║${RESET}"
echo -e "${GREEN}${BOLD}   ██║   █████╗  ██████╔╝██╔████╔██║${RESET}"
echo -e "${GREEN}${BOLD}   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║${RESET}"
echo -e "${GREEN}${BOLD}   ██║   ███████╗██║  ██║██║ ╚═╝ ██║${RESET}"
echo -e "${GREEN}${BOLD}   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝${RESET}"
echo -e "${CYAN}${BOLD}  AUTO INSTALLER v5.2 OPTIMIZED${RESET}"
echo -e "${RED}  [!] Only use on systems you own/are authorized${RESET}\n"

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Please run as root: sudo ./install.sh${RESET}"
    exit 1
fi

# Detect OS
if [ -f /etc/debian_version ]; then
    PKG_MANAGER="apt"
    echo -e "${GREEN}[✓] Detected Debian/Ubuntu/Kali/Parrot system${RESET}"
elif [ -f /etc/arch-release ]; then
    PKG_MANAGER="pacman"
    echo -e "${GREEN}[✓] Detected Arch-based system${RESET}"
elif [ -f /etc/fedora-release ]; then
    PKG_MANAGER="dnf"
    echo -e "${GREEN}[✓] Detected Fedora-based system${RESET}"
else
    PKG_MANAGER="apt"
    echo -e "${YELLOW}[!] Unknown OS, defaulting to apt${RESET}"
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 1: SYSTEM UPDATE${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if [ "$PKG_MANAGER" = "apt" ]; then apt update && apt upgrade -y
elif [ "$PKG_MANAGER" = "pacman" ]; then pacman -Syu --noconfirm
elif [ "$PKG_MANAGER" = "dnf" ]; then dnf update -y
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 2: PYTHON & PIP${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if [ "$PKG_MANAGER" = "apt" ]; then apt install -y python3 python3-pip python3-venv
elif [ "$PKG_MANAGER" = "pacman" ]; then pacman -S --noconfirm python python-pip
elif [ "$PKG_MANAGER" = "dnf" ]; then dnf install -y python3 python3-pip
fi
echo -e "${GREEN}[✓] Python3 installed: $(python3 --version)${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 3: PYTHON PACKAGES (pip)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
pip3 install --upgrade pip
pip3 install -r requirements.txt
echo -e "${GREEN}[✓] Python packages installed${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 4: CORE SECURITY TOOLS (apt)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if [ "$PKG_MANAGER" = "apt" ]; then
    apt install -y \
        nmap nikto gobuster sslscan sqlmap proxychains4 tor torsocks \
        whois dnsutils curl wget git seclists theharvester wpscan
fi
echo -e "${GREEN}[✓] Core security tools installed${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 5: GO LANGUAGE (Required for ProjectDiscovery)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if ! command -v go &> /dev/null; then
    echo -e "${YELLOW}[*] Installing Go...${RESET}"
    if [ "$PKG_MANAGER" = "apt" ]; then apt install -y golang-go
    elif [ "$PKG_MANAGER" = "pacman" ]; then pacman -S --noconfirm go
    elif [ "$PKG_MANAGER" = "dnf" ]; then dnf install -y golang
    fi
fi
echo -e "${GREEN}[✓] Go installed: $(go version)${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 6: PROJECTDISCOVERY TOOLS (Go)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
export PATH=$PATH:$(go env GOPATH)/bin
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest
echo -e "${GREEN}[✓] ProjectDiscovery tools installed${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 7: AMASS & FFUF (Go)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
go install github.com/owasp-amass/amass/v4@latest
go install github.com/ffuf/ffuf/v2@latest
echo -e "${GREEN}[✓] Amass and FFUF installed${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 8: RUSTSCAN (Rust-based fast scanner)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if ! command -v rustscan &> /dev/null; then
    echo -e "${YELLOW}[*] Installing RustScan...${RESET}"
    if [ "$PKG_MANAGER" = "apt" ]; then
        apt install -y rustscan 2>/dev/null || {
            echo -e "${YELLOW}[*] Apt failed, trying .deb package...${RESET}"
            wget -q -O /tmp/rustscan.deb https://github.com/RustScan/RustScan/releases/latest/download/rustscan_2.3.0_amd64.deb
            dpkg -i /tmp/rustscan.deb || apt --fix-broken install -y
        }
    elif [ "$PKG_MANAGER" = "pacman" ]; then pacman -S --noconfirm rustscan
    elif [ "$PKG_MANAGER" = "dnf" ]; then dnf install -y rustscan
    fi
fi
if command -v rustscan &> /dev/null; then
    echo -e "${GREEN}[✓] RustScan installed: $(rustscan --version)${RESET}"
else
    echo -e "${RED}[!] RustScan installation failed. Please install manually.${RESET}"
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 9: TOR & PROXYCHAINS CONFIGURATION${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
TORRC="/etc/tor/torrc"
if [ -f "$TORRC" ]; then
    if ! grep -q "^ControlPort 9051" "$TORRC"; then
        echo -e "\n# Security Hub - Tor Control Port" >> "$TORRC"
        echo "ControlPort 9051" >> "$TORRC"
        echo "CookieAuthentication 1" >> "$TORRC"
        echo -e "${GREEN}[✓] Tor Control Port (9051) enabled${RESET}"
    fi
fi

PC_CONF="/etc/proxychains4.conf"
if [ -f "$PC_CONF" ]; then
    if ! grep -q "socks5 127.0.0.1 9050" "$PC_CONF"; then
        echo "socks5 127.0.0.1 9050" >> "$PC_CONF"
        echo -e "${GREEN}[✓] Proxychains configured for Tor SOCKS5${RESET}"
    fi
fi

systemctl enable tor 2>/dev/null || true
systemctl start tor 2>/dev/null || true
echo -e "${GREEN}[✓] Tor service started${RESET}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 10: NUCLEI TEMPLATES UPDATE${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if command -v nuclei &> /dev/null; then
    nuclei -update-templates
    echo -e "${GREEN}[✓] Nuclei templates updated${RESET}"
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  STEP 11: CREATE OUTPUT DIRECTORY${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
mkdir -p output
echo -e "${GREEN}[✓] output/ directory created${RESET}"

echo -e "\n${GREEN}${BOLD}╔════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║            INSTALLATION COMPLETE!                       ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════╝${RESET}"
echo -e "\n  Run the toolkit:"
echo -e "  ${CYAN}${BOLD}python3 toolkit.py${RESET}"
echo -e "\n  ${RED}${BOLD}  ⚠  ONLY use on assets you OWN or have PERMISSION to test!${RESET}\n"