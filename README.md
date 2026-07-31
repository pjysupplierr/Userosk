#  Ultimate Security Hub (USH) 

```text
██╗   ██╗███████╗███████╗██████╗  ██████╗ ███████╗██╗  ██╗
██║   ██║██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝
██║   ██║███████╗█████╗  ██████╔╝██║   ██║███████╗█████╔╝ 
██║   ██║╚════██║██╔══╝  ██╔══██╗██║   ██║╚════██║██╔═██╗ 
╚██████╔╝███████║███████╗██║  ██║╚██████╔╝███████║██║  ██╗
 ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
              ULTIMATE SECURITY HUB v5.2 ELITE
```

[![Language](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Shell](https://img.shields.io/badge/Bash-4.0%2B-green.svg)](https://www.gnu.org/software/bash/)
[![Platform](https://img.shields.io/badge/OS-Linux%20%7C%20Kali%20%7C%20Parrot-black.svg)](https://www.kali.org/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

An all-in-one automated reconnaissance, vulnerability scanning, and OSINT framework designed for penetration testers, bug bounty hunters, and security auditors. **USH v5.2 Elite** orchestrates industry-standard security tools into a unified CLI interface featuring automated dependency resolution, Tor IP rotation, target-based output organization, and automated report generation.

---

##  Table of Contents

- [Key Features](#-key-features)
- [Architecture & Integrated Tools](#-architecture--integrated-tools)
- [Prerequisites](#-prerequisites)
- [Step-by-Step Installation](#-step-by-step-installation)
  - [Option A: Automated Setup (Recommended)](#option-a-automated-setup-recommended)
  - [Option B: Manual Installation](#option-b-manual-installation)
- [Usage Guide](#-usage-guide)
  - [Starting the Toolkit](#1-starting-the-toolkit)
  - [Tor Anonymity & Proxy Configuration](#2-tor-anonymity--proxy-configuration)
  - [Scanning & Recon Modules](#3-scanning--recon-modules)
- [Target Management & Reporting](#-target-management--reporting)
- [Troubleshooting](#-troubleshooting)
- [Legal Disclaimer](#-legal-disclaimer)

---

##  Key Features

- **Automated Dependency Engine:** Automatically checks for missing tools (`nmap`, `rustscan`, `nuclei`, `subfinder`, `httpx`, `dnsx`, `ffuf`, `amass`, `gobuster`, `nikto`, `sqlmap`, `wpscan`) and offers real-time one-click fixes.
- **Tor Anonymity Core:** Route scans through Tor with SOCKS5 / Proxychains4 integration. Includes manual (`NEWNYM`) and scheduled automatic IP rotation threads.
- **Structured Output Vault:** Automatically organizes logs, outputs, and JSON dumps into dedicated target directories (`output/<target_name>/`).
- **Markdown Executive Report Generator:** Compiles raw scan outputs into clean, consolidated markdown reports (`_REPORT_<timestamp>.md`) for documentation and deliverable submission.
- **Multi-Distro Compatibility:** Auto-detects package managers (`apt`, `pacman`, `dnf`) across Kali Linux, Parrot OS, Ubuntu, Debian, Arch, and Fedora.

---

##  Architecture & Integrated Tools

| Module | Engine / Tool | Description |
| :--- | :--- | :--- |
| **Network Recon** | `Nmap`, `RustScan`, `NSLookup`, `Dig` | Fast/full port scanning, OS fingerprinting, DNS record resolution |
| **Subdomain Enumeration** | `Subfinder`, `Amass`, `dnsx` | Passive and active subdomain discovery, DNS brute-forcing |
| **Web Recon & Fingerprinting** | `httpx`, `Nikto`, `Title Grabber` | Tech stack identification, HTTP header analysis, web server vulnerability auditing |
| **Fuzzing & Directory Discovery** | `FFUF`, `Gobuster` | High-speed directory, file, and virtual host brute-forcing |
| **Vulnerability Scanning** | `Nuclei` (v3) | Automated CVE and misconfiguration scanning with auto-updating templates |
| **CMS & Database Assessment** | `WPScan`, `SQLMap` | WordPress vulnerability checking and SQL injection auditing |
| **OSINT & Threat Intel** | `python-whois`, `Shodan`, `Censys` | WHOIS lookups and API-driven internet-wide asset discovery |

---
<img width="650" height="665" alt="image" src="https://github.com/user-attachments/assets/d3fa9790-7030-4aaf-a960-c5fb25cbf2f8" />

##  Prerequisites

Ensure your system meets the following requirements before installation:

- **Operating System:** Linux (Kali Linux, Parrot OS, Ubuntu 20.04+, Debian 11+, Arch Linux, Fedora)
- **Python:** `3.8`
