#!/usr/bin/env python3
"""
USH - ULTIMATE SECURITY HUB v5.2 ELITE
Hacker Edition | Auto-Save | Target Folders | Advanced Auto-Fix Engine
ONLY USE ON ASSETS YOU OWN OR HAVE PERMISSION TO TEST
"""
import socket
import subprocess
import requests
import sys
import re
import os
import time
import threading
import shutil
import json
import random
import tempfile
from requests.auth import HTTPBasicAuth
from datetime import datetime

# ── OS DETECTION ──
IS_WINDOWS = os.name == 'nt'
IS_LINUX = os.name == 'posix'

try:
    from stem import Signal
    from stem.control import Controller
    HAS_STEM = True
except ImportError:
    HAS_STEM = False

# ── COLORS ──
RST, BOLD, DIM = '\033[0m', '\033[1m', '\033[2m'
RED, GRN, YLW, BLU, MGN, CYN, WHT = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m'

# ── GLOBAL STATE ──
USE_TOR = False
TARGET = ""
TARGET_IP = ""
TARGET_FOLDER = ""
SHODAN_KEY = ""
CENSYS_ID = ""
CENSYS_SECRET = ""
auto_rotate_thread = None
stop_rotate_event = threading.Event()

# ════════════════════════════════════════════════
#  ADVANCED AUTO-FIX ENGINE
# ════════════════════════════════════════════════
TOOL_FIXES = {
    "nmap": ("sudo apt install nmap -y", "Installing Nmap via apt..."),
    "rustscan": ("sudo apt install rustscan -y || (wget -qO /tmp/rustscan.deb https://github.com/RustScan/RustScan/releases/latest/download/rustscan_2.3.0_amd64.deb && sudo dpkg -i /tmp/rustscan.deb)", "Installing RustScan..."),
    "nuclei": ("go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "Compiling Nuclei via Go..."),
    "subfinder": ("go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "Compiling Subfinder via Go..."),
    "httpx": ("go install github.com/projectdiscovery/httpx/cmd/httpx@latest", "Compiling httpx via Go..."),
    "dnsx": ("go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest", "Compiling dnsx via Go..."),
    "ffuf": ("go install github.com/ffuf/ffuf/v2@latest", "Compiling FFUF via Go..."),
    "amass": ("go install github.com/owasp-amass/amass/v4@latest", "Compiling Amass via Go..."),
    "gobuster": ("sudo apt install gobuster -y", "Installing Gobuster via apt..."),
    "nikto": ("sudo apt install nikto -y", "Installing Nikto via apt..."),
    "sqlmap": ("sudo apt install sqlmap -y", "Installing SQLMap via apt..."),
    "wpscan": ("sudo apt install wpscan -y", "Installing WPScan via apt..."),
    "proxychains4": ("sudo apt install proxychains4 -y", "Installing Proxychains4..."),
    "python-whois": ("pip3 install python-whois", "Installing python-whois via pip..."),
    "dnspython": ("pip3 install dnspython", "Installing dnspython via pip..."),
}

def prompt_auto_fix(tool_name):
    """High-tech prompt to auto-fix a missing or broken tool."""
    print(f"\n  {RED}{BOLD}[!] CRITICAL: {tool_name.upper()} is missing or failed.{RST}")
    if tool_name in TOOL_FIXES:
        print(f"  {CYN}[→] Available Fix: {TOOL_FIXES[tool_name][1]}{RST}")
        choice = input(f"  {YLW}Execute Auto-Fix? (y/n): {RST}").strip().lower()
        if choice in ['y', 'yes']:
            launch_anim(f"Auto-Fixing {tool_name}", "🔧")
            cmd = TOOL_FIXES[tool_name][0]
            try:
                # Run with shell=True to handle pipes (||) and sudo prompts interactively
                subprocess.run(cmd, shell=True, check=True)
                # Update PATH for Go tools without restarting
                os.environ["PATH"] += os.pathsep + subprocess.getoutput("go env GOPATH") + "/bin"
                if check_tool(tool_name) or tool_name in ["python-whois", "dnspython"]:
                    ok(f"{tool_name} successfully installed and verified!")
                    time.sleep(1)
                    return True
                else:
                    fail(f"Fix executed, but {tool_name} is still not found in PATH.")
                    return False
            except subprocess.CalledProcessError:
                fail(f"Auto-fix failed. You may need to install {tool_name} manually.")
                return False
    else:
        print(f"  {YLW}[!] No automated fix available for {tool_name}. Please install manually.{RST}")
    return False

def auto_fix_all_missing():
    """Scans for all missing tools and offers to fix them."""
    section("AUTO-FIX ALL MISSING TOOLS", "🛠")
    missing = [name for name in TOOL_FIXES.keys() if not check_tool(name)]
    if not missing:
        ok("All tracked tools are already installed!")
        input(f"\n{DIM}Enter to continue...{RST}")
        return
    
    print(f"  {YLW}Found {len(missing)} missing tools:{RST}")
    for m in missing: print(f"    {RED}✗{RST} {m}")
    
    choice = input(f"\n  {CYN}Install ALL missing tools automatically? (y/n): {RST}").strip().lower()
    if choice in ['y', 'yes']:
        for tool in missing:
            print(f"\n{CYN}{'─'*60}{RST}")
            prompt_auto_fix(tool)
        ok("Auto-fix sequence complete. Please restart the tool if Go tools were installed.")
    input(f"\n{DIM}Enter to continue...{RST}")

# ════════════════════════════════════════════════
#  AUTO-SAVE & REPORTING ENGINE
# ════════════════════════════════════════════════
def make_target_folder(target):
    safe_name = re.sub(r'[^\w\.\-]', '_', target)
    folder = os.path.join("output", safe_name)
    os.makedirs(folder, exist_ok=True)
    return folder

def auto_save(section, content):
    global TARGET_FOLDER
    if not TARGET_FOLDER or not content: return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{TARGET_FOLDER}/{section}_{ts}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n  {section.upper()} SCAN\n  Target: {TARGET}\n  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n  Tor: {'ON' if USE_TOR else 'OFF'}\n{'='*60}\n")
        f.write(content)
        f.write(f"\n{'='*60}\n")

def auto_save_json(section, data):
    global TARGET_FOLDER
    if not TARGET_FOLDER or not data: return
    filename = f"{TARGET_FOLDER}/{section}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def generate_markdown_report():
    global TARGET_FOLDER
    if not TARGET_FOLDER: return
    section("GENERATING MARKDOWN REPORT", "📝")
    md_file = os.path.join(TARGET_FOLDER, f"_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(md_file, "w", encoding="utf-8") as md:
        md.write(f"# Security Assessment Report: {TARGET}\n")
        md.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Tor:** {'Yes' if USE_TOR else 'No'}\n\n")
        md.write("## Executive Summary\nThis report contains automated reconnaissance results.\n\n## Findings\n")
        for file in sorted(os.listdir(TARGET_FOLDER)):
            if file.endswith('.txt') and not file.startswith('_'):
                with open(os.path.join(TARGET_FOLDER, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    md.write(f"### {file.replace('.txt', '').replace('_', ' ').title()}\n```\n")
                    md.write(content[:2000] + ("...\n[Truncated]" if len(content) > 2000 else ""))
                    md.write("\n```\n\n")
    ok(f"Markdown report saved to: {CYN}{md_file}{RST}")

def clear_target_output():
    global TARGET_FOLDER
    if not TARGET_FOLDER or not os.path.exists(TARGET_FOLDER):
        warn("No target folder exists yet."); return
    confirm = input(f"  {RED}Delete ALL files in {TARGET_FOLDER}? (y/n): {RST}").strip().lower()
    if confirm == 'y':
        for f in os.listdir(TARGET_FOLDER): os.remove(os.path.join(TARGET_FOLDER, f))
        ok("Output folder cleared successfully.")

# ════════════════════════════════════════════════
#  VISUAL ENGINE
# ════════════════════════════════════════════════
def clear(): os.system('cls' if IS_WINDOWS else 'clear')

def banner():
    print(f"""{GRN}{BOLD}
██╗   ██╗███████╗███████╗██████╗  ██████╗ ███████╗██╗  ██╗
██║   ██║██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝
██║   ██║███████╗█████╗  ██████╔╝██║   ██║███████╗█████╔╝ 
██║   ██║╚════██║██╔══╝  ██╔══██╗██║   ██║╚════██║██╔═██╗ 
╚██████╔╝███████║███████╗██║  ██║╚██████╔╝███████║██║  ██╗
 ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝{RST}
{CYN}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ULTIMATE SECURITY HUB v5.2 ELITE  │  Auto-Fix Engine Active
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RST}
{RED}  ONLY USE ON ASSETS YOU OWN OR HAVE PERMISSION TO TEST{RST}
""")

def section(title, icon="◈"):
    print(f"\n{MGN}{BOLD}{'━'*60}\n  {icon} {title}\n{'━'*60}{RST}\n")

def ok(msg):   print(f"  {GRN}[✓]{RST} {msg}")
def fail(msg): print(f"  {RED}[✗]{RST} {msg}")
def warn(msg): print(f"  {YLW}[!]{RST} {msg}")
def info(msg): print(f"  {CYN}[→]{RST} {msg}")

def status(label, value, st="info"):
    c = {"ok": GRN, "fail": RED, "warn": YLW, "info": CYN}.get(st, CYN)
    print(f"  {c}┃{RST} {BOLD}{label:<24}{RST} {value}")

def sep(ch="─", w=60, color=DIM): print(f"{color}{ch*w}{RST}")

def launch_anim(name, icon="⚡"):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    sys.stdout.write(f"  {CYN}{icon} {BOLD}{name}{RST} ")
    for f in frames:
        sys.stdout.write(f"\r  {CYN}{icon} {f} {BOLD}{name}{RST} ")
        sys.stdout.flush(); time.sleep(0.05)
    sys.stdout.write(f"\r  {GRN}{icon} {BOLD}{name} COMPLETE{RST}\n")
    sys.stdout.flush()

def prompt(name="USH"): return input(f"  {GRN}┌──({RED}{name}{GRN})─[{CYN}~{GRN}]\n└────➤ {RST}").strip()
def numbered_list(items, color=CYN):
    for i, item in enumerate(items, 1): print(f"  {color}{i:>3}{RST}  {item}")

# ════════════════════════════════════════════════
#  UTILITY & TOR ENGINE
# ════════════════════════════════════════════════
def check_tool(name): return shutil.which(name) is not None
def get_proxies(): return {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"} if USE_TOR else {}
def get_cli_prefix(): return ['proxychains4', '-q'] if USE_TOR and IS_LINUX and check_tool('proxychains4') else []

def check_tor_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2); s.connect(("127.0.0.1", 9050)); s.close()
        return True
    except: return False

def get_tor_ip():
    try:
        r = requests.get("https://check.torproject.org/api/ip", proxies=get_proxies(), timeout=10)
        return r.json().get("IP", "Unknown")
    except: return "Error"

def rotate_tor_ip():
    info("Sending NEWNYM signal...")
    if HAS_STEM:
        try:
            with Controller.from_port(port=9051) as c:
                c.authenticate(); c.signal(Signal.NEWNYM)
                ok("NEWNYM sent via Stem. Waiting 10s..."); time.sleep(10); return True
        except: pass
    if IS_LINUX:
        try:
            subprocess.run(['sudo', 'killall', '-HUP', 'tor'], check=True, capture_output=True)
            ok("Tor reloaded. Waiting 10s..."); time.sleep(10); return True
        except: pass
    warn("Rotation failed. Restart Tor manually."); return False

def auto_rotate_worker(interval):
    while not stop_rotate_event.is_set():
        rotate_tor_ip()
        stop_rotate_event.wait(interval)

def start_auto_rotate(interval):
    global auto_rotate_thread
    if auto_rotate_thread and auto_rotate_thread.is_alive(): stop_rotate_event.set(); auto_rotate_thread.join()
    stop_rotate_event.clear()
    auto_rotate_thread = threading.Thread(target=auto_rotate_worker, args=(interval,), daemon=True)
    auto_rotate_thread.start()
    ok(f"Auto-rotation every {interval}s started")

def stop_auto_rotate():
    global auto_rotate_thread
    if auto_rotate_thread and auto_rotate_thread.is_alive():
        stop_rotate_event.set(); auto_rotate_thread.join()
        ok("Auto-rotation stopped")
    else: warn("Auto-rotation not running")

def tor_submenu():
    global USE_TOR
    while True:
        section("TOR ANONYMITY & IP ROTATION", "🧅")
        tor_st = f"{GRN}{BOLD}◉ ON{RST}" if USE_TOR else f"{RED}○ OFF{RST}"
        status("Tor Routing", tor_st, "ok" if USE_TOR else "fail")
        if USE_TOR: status("Exit IP", f"{CYN}{BOLD}{get_tor_ip()}{RST}", "info")
        else: status("Exit IP", f"{DIM}N/A{RST}", "warn")
        sep()
        numbered_list(["Toggle Tor ON/OFF", "Rotate IP Now (NEWNYM)", "Start Auto-Rotation", "Stop Auto-Rotation", "Back"], MGN)
        sep()
        ch = prompt("TOR")
        if ch == "1":
            USE_TOR = not USE_TOR
            if USE_TOR and not check_tor_service():
                fail("Tor SOCKS port (9050) not listening!"); info("Fix: sudo systemctl start tor"); USE_TOR = False
            elif USE_TOR: ok(f"Tor ENABLED — Exit IP: {get_tor_ip()}")
            else: ok("Tor DISABLED")
            input(f"\n{DIM}Enter to continue...{RST}")
        elif ch == "2":
            if not USE_TOR: fail("Enable Tor first!")
            else: old = get_tor_ip(); rotate_tor_ip(); ok(f"IP: {old} → {get_tor_ip()}")
            input(f"\n{DIM}Enter to continue...{RST}")
        elif ch == "3":
            if not USE_TOR: fail("Enable Tor first!")
            else:
                try: start_auto_rotate(int(input(f"  {CYN}Interval seconds (e.g. 60): {RST}").strip()))
                except ValueError: fail("Invalid number")
            input(f"\n{DIM}Enter to continue...{RST}")
        elif ch == "4": stop_auto_rotate(); input(f"\n{DIM}Enter to continue...{RST}")
        elif ch == "5": break

# ════════════════════════════════════════════════
#  SCAN / ATTACK FUNCTIONS (With Auto-Fix Integration)
# ════════════════════════════════════════════════
def resolve_ip(target):
    info(f"Resolving {BOLD}{target}{RST}")
    if USE_TOR and IS_LINUX and check_tool('tor-resolve'):
        try:
            r = subprocess.run(['tor-resolve', target, '127.0.0.1:9050'], capture_output=True, text=True, check=True, timeout=10)
            ok(f"IP via Tor: {CYN}{BOLD}{r.stdout.strip()}{RST}"); return r.stdout.strip()
        except: pass
    try:
        ip = socket.gethostbyname(target); ok(f"IP: {CYN}{BOLD}{ip}{RST}"); return ip
    except socket.gaierror:
        fail("Could not resolve hostname"); return None

def attack_website_title(target):
    launch_anim("Website Title Grab", "🌐")
    url = target if target.startswith('http') else f"http://{target}"
    output = ""
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, proxies=get_proxies())
        m = re.search(r'<title>(.*?)</title>', r.text, re.IGNORECASE)
        title = m.group(1).strip() if m else "Not found"
        ok(f"Title: {CYN}{BOLD}{title}{RST} | Status: {r.status_code}")
        output = f"Title: {title}\nStatus: {r.status_code}\nServer: {r.headers.get('Server', 'Unknown')}\n"
    except Exception as e:
        fail(f"Error: {e}"); output = f"Error: {e}\n"
    auto_save("title", output); return output

def attack_nslookup(target):
    launch_anim("NSLookup", "🔍")
    try:
        r = subprocess.run(['nslookup', target], capture_output=True, text=True, check=True)
        print(f"\n{DIM}{r.stdout}{RST}\n"); auto_save("nslookup", r.stdout); return r.stdout
    except: fail("NSLookup failed"); return "NSLookup failed\n"

def attack_dnsx(target):
    if not check_tool('dnsx'):
        if not prompt_auto_fix('dnsx'): return ""
        return attack_dnsx(target)
    launch_anim("dnsx", "🔍")
    try:
        cmd = get_cli_prefix() + ['dnsx', '-d', target, '-a', '-resp', '-silent']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        print(f"\n{DIM}{r.stdout}{RST}\n"); auto_save("dnsx", r.stdout); return r.stdout
    except Exception as e: fail(f"dnsx: {e}"); return f"Error: {e}\n"

def attack_dns_enum(target):
    launch_anim("DNS Enumeration", "🗂")
    output = ""
    try:
        import dns.resolver
        for rt in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']:
            try:
                answers = dns.resolver.resolve(target, rt)
                for rdata in answers:
                    line = f"[{rt}] {rdata}"; ok(line); output += line + "\n"
            except: warn(f"[{rt}] No records"); output += f"[{rt}] No records\n"
    except ImportError:
        warn("dnspython not installed. Falling back to 'dig'...")
        if check_tool('dig'):
            try:
                r = subprocess.run(['dig', 'ANY', target], capture_output=True, text=True, check=True, timeout=30)
                print(f"\n{DIM}{r.stdout}{RST}\n"); output = r.stdout
            except: output = "dig failed\n"
        else: output = "dnspython and dig unavailable\n"
    auto_save("dns_enum", output); return output

def attack_nmap(target):
    if not check_tool('nmap'):
        if not prompt_auto_fix('nmap'): return ""
        return attack_nmap(target)
    launch_anim("Nmap Fast Scan", "🛡")
    try:
        cmd = get_cli_prefix() + ['nmap', '-F', '-O', target]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("\n")
        for line in r.stdout.split('\n'):
            if 'open' in line.lower(): print(f"  {GRN}{line}{RST}")
            elif 'closed' in line.lower(): print(f"  {RED}{line}{RST}")
            else: print(f"  {DIM}{line}{RST}")
        print("\n")
        auto_save("nmap", r.stdout); return r.stdout
    except Exception as e: fail(f"Nmap: {e}"); return f"Error: {e}\n"

def attack_rustscan(target):
    if not check_tool('rustscan'):
        if not prompt_auto_fix('rustscan'): return ""
        return attack_rustscan(target)
    launch_anim("RustScan (Ultra-Fast)", "⚡")
    try:
        cmd = get_cli_prefix() + ['rustscan', '-a', target, '--', 'nmap', '-Pn', '-sV', '-F']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
        print(f"\n{CYN}{r.stdout}{RST}\n")
        auto_save("rustscan", r.stdout); return r.stdout
    except Exception as e: fail(f"RustScan: {e}"); return f"Error: {e}\n"

def attack_nmap_full(target):
    if not check_tool('nmap'):
        if not prompt_auto_fix('nmap'): return ""
        return attack_nmap_full(target)
    launch_anim("Nmap Full Scan (All 65535 Ports)", "💀")
    try:
        cmd = get_cli_prefix() + ['nmap', '-p-', '-sV', '-O', target]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=3600)
        print("\n")
        for line in r.stdout.split('\n'):
            if 'open' in line.lower(): print(f"  {GRN}{line}{RST}")
            else: print(f"  {DIM}{line}{RST}")
        print("\n")
        auto_save("nmap_full", r.stdout); return r.stdout
    except subprocess.TimeoutExpired:
        fail("Nmap full scan timed out (>1hr). Check partial output."); return "Nmap full scan timed out\n"
    except Exception as e: fail(f"Nmap full: {e}"); return f"Error: {e}\n"

def attack_nikto(target):
    if not check_tool('nikto'):
        if not prompt_auto_fix('nikto'): return ""
        return attack_nikto(target)
    launch_anim("Nikto", "🔓")
    url = target if target.startswith('http') else f"http://{target}"
    try:
        cmd = get_cli_prefix() + ['nikto', '-h', url, '-Display', '12EP']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        print("\n")
        for line in r.stdout.split('\n'):
            if 'OSVDB' in line or 'vuln' in line.lower(): print(f"  {RED}{BOLD}{line}{RST}")
            else: print(f"  {DIM}{line}{RST}")
        print("\n")
        auto_save("nikto", r.stdout); return r.stdout
    except Exception as e: fail(f"Nikto: {e}"); return f"Error: {e}\n"

def attack_httpx(target):
    if not check_tool('httpx'):
        if not prompt_auto_fix('httpx'): return ""
        return attack_httpx(target)
    launch_anim("httpx", "🌐")
    url = target if target.startswith('http') else f"http://{target}"
    try:
        cmd = get_cli_prefix() + ['httpx', '-u', url, '-title', '-tech-detect', '-status-code', '-silent']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        print(f"\n{CYN}{r.stdout}{RST}\n")
        auto_save("httpx", r.stdout); return r.stdout
    except Exception as e: fail(f"httpx: {e}"); return f"Error: {e}\n"

def attack_nuclei(target):
    if not check_tool('nuclei'):
        if not prompt_auto_fix('nuclei'): return ""
        return attack_nuclei(target)
    launch_anim("Nuclei", "☢")
    url = target if target.startswith('http') else f"http://{target}"
    try:
        cmd = get_cli_prefix() + ['nuclei', '-u', url, '-silent']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
        print("\n")
        for line in r.stdout.split('\n'):
            if 'critical' in line.lower() or 'high' in line.lower(): print(f"  {RED}{BOLD}{line}{RST}")
            elif 'medium' in line.lower(): print(f"  {YLW}{line}{RST}")
            elif line.strip(): print(f"  {GRN}{line}{RST}")
        print("\n")
        auto_save("nuclei", r.stdout); return r.stdout
    except Exception as e: fail(f"Nuclei: {e}"); return f"Error: {e}\n"

def attack_subfinder(target):
    if not check_tool('subfinder'):
        if not prompt_auto_fix('subfinder'): return ""
        return attack_subfinder(target)
    launch_anim("Subfinder", "🔎")
    try:
        cmd = get_cli_prefix() + ['subfinder', '-d', target, '-silent']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        subs = r.stdout.strip().split('\n')
        ok(f"Found {BOLD}{len(subs)}{RST} subdomains")
        for s in subs[:20]: print(f"    {CYN}├──{RST} {s}")
        if len(subs) > 20: print(f"    {CYN}└──{RST} {DIM}...and {len(subs)-20} more{RST}")
        auto_save_json("subdomains", {"count": len(subs), "subdomains": subs})
        return r.stdout
    except Exception as e: fail(f"Subfinder: {e}"); return f"Error: {e}\n"

def attack_gobuster(target):
    if not check_tool('gobuster'):
        if not prompt_auto_fix('gobuster'): return ""
        return attack_gobuster(target)
    launch_anim("Gobuster", "📂")
    url = target if target.startswith('http') else f"http://{target}"
    paths = ["/usr/share/wordlists/dirb/common.txt", "/usr/share/seclists/Discovery/Web-Content/common.txt", "common.txt"]
    wl = next((p for p in paths if os.path.exists(p)), None)
    if not wl:
        wl = os.path.join(tempfile.gettempdir(), 'ush_fallback_wl.txt')
        with open(wl, 'w') as f: f.write('\n'.join(["admin","login","wp-admin","api","backup","test","dev","config"]))
    try:
        cmd = get_cli_prefix() + ['gobuster', 'dir', '-u', url, '-w', wl, '-q', '-x', 'txt,php,html,bak']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        print("\n")
        for line in r.stdout.split('\n'):
            if '200' in line: print(f"  {GRN}{line}{RST}")
            elif '403' in line: print(f"  {YLW}{line}{RST}")
            elif line.strip(): print(f"  {DIM}{line}{RST}")
        print("\n")
        auto_save("gobuster", r.stdout); return r.stdout
    except Exception as e: fail(f"Gobuster: {e}"); return f"Error: {e}\n"

def attack_ffuf(target):
    if not check_tool('ffuf'):
        if not prompt_auto_fix('ffuf'): return ""
        return attack_ffuf(target)
    launch_anim("FFUF (Fast Web Fuzzer)", "🚀")
    url = target if target.startswith('http') else f"http://{target}"
    paths = ["/usr/share/seclists/Discovery/Web-Content/common.txt", "common.txt"]
    wl = next((p for p in paths if os.path.exists(p)), None)
    if not wl:
        wl = os.path.join(tempfile.gettempdir(), 'ush_fallback_wl.txt')
        with open(wl, 'w') as f: f.write('\n'.join(["admin","login","api","backup","test","dev","config"]))
    try:
        cmd = get_cli_prefix() + ['ffuf', '-u', f"{url}/FUZZ", '-w', wl, '-mc', '200,204,301,302,307,401,403', '-t', '50', '-s']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        print(f"\n{CYN}{r.stdout}{RST}\n")
        auto_save("ffuf", r.stdout); return r.stdout
    except Exception as e: fail(f"FFUF: {e}"); return f"Error: {e}\n"

def attack_wpscan(target):
    if not check_tool('wpscan'):
        if not prompt_auto_fix('wpscan'): return ""
        return attack_wpscan(target)
    launch_anim("WPScan", "🔍")
    url = target if target.startswith('http') else f"http://{target}"
    output = ""
    try:
        cmd = get_cli_prefix() + ['wpscan', '--url', url, '--random-user-agent', '--no-update', '--stealthy']
        r = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
        print(f"\n{CYN}{r.stdout}{RST}\n")
        output = r.stdout
    except subprocess.TimeoutExpired:
        fail("WPScan timed out"); output = "WPScan timed out\n"
    except Exception as e:
        fail(f"WPScan: {e}"); output = f"Error: {e}\n"
    auto_save("wpscan", output); return output

def attack_whois(target):
    launch_anim("WHOIS Lookup", "📄")
    output = ""
    try:
        import whois
        data = whois.whois(target)
        fields = ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'name_servers', 'emails', 'org']
        for f in fields:
            val = getattr(data, f, None)
            if val: ok(f"{f}: {val}"); output += f"{f}: {val}\n"
        output += "\n"
        auto_save_json("whois", {f: str(getattr(data, f, None)) for f in fields})
    except ImportError:
        warn("python-whois not installed. Falling back to CLI...")
        if check_tool('whois'):
            try:
                r = subprocess.run(['whois', target], capture_output=True, text=True, check=True, timeout=30)
                print(f"\n{DIM}{r.stdout}{RST}\n"); output = r.stdout
            except: fail("whois command failed"); output = "whois failed\n"
        else: fail("whois not available"); output = "whois unavailable\n"
    except Exception as e:
        fail(f"WHOIS: {e}"); output = f"Error: {e}\n"
    auto_save("whois", output); return output

def attack_shodan(ip):
    global SHODAN_KEY
    if not SHODAN_KEY: SHODAN_KEY = input(f"  {CYN}Enter Shodan API Key: {RST}").strip()
    if not SHODAN_KEY: warn("No Shodan key provided."); return ""
    launch_anim("Shodan", "👁")
    try:
        r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}", timeout=10, proxies=get_proxies())
        if r.status_code == 200:
            data = r.json()
            status("Organization", f"{CYN}{data.get('org','N/A')}{RST}", "info")
            status("Open Ports", f"{GRN}{', '.join(map(str, data.get('ports',[])))}{RST}", "ok")
            vulns = data.get('vulns', [])
            if vulns:
                print(f"  {RED}{BOLD}⚠ CVEs:{RST}")
                for v in vulns[:10]: print(f"    {RED}├──{RST} {v}")
            else: ok("No CVEs tagged")
            auto_save_json("shodan", data); return json.dumps(data, indent=2)
        else: fail(f"Shodan API Error: {r.status_code}"); return f"API Error: {r.status_code}\n"
    except Exception as e: fail(f"Shodan: {e}"); return f"Error: {e}\n"

def attack_censys(ip):
    global CENSYS_ID, CENSYS_SECRET
    if not CENSYS_ID: CENSYS_ID = input(f"  {CYN}Enter Censys API ID: {RST}").strip()
    if not CENSYS_SECRET: CENSYS_SECRET = input(f"  {CYN}Enter Censys API Secret: {RST}").strip()
    if not CENSYS_ID or not CENSYS_SECRET: warn("No Censys credentials."); return ""
    launch_anim("Censys", "🔭")
    try:
        r = requests.get(f"https://search.censys.io/api/v2/hosts/{ip}", auth=HTTPBasicAuth(CENSYS_ID, CENSYS_SECRET), timeout=10, proxies=get_proxies())
        if r.status_code == 200:
            svcs = r.json().get('result',{}).get('services',[])
            ok(f"Found {BOLD}{len(svcs)}{RST} services")
            for s in svcs[:5]: print(f"    {MGN}├──{RST} Port {s.get('port')}: {s.get('service_name','Unknown')}")
            auto_save_json("censys", r.json()); return json.dumps(r.json(), indent=2)
        else: fail(f"Censys API Error: {r.status_code}"); return f"API Error: {r.status_code}\n"
    except Exception as e: fail(f"Censys: {e}"); return f"Error: {e}\n"

def attack_sqlmap(target):
    if not check_tool('sqlmap'):
        if not prompt_auto_fix('sqlmap'): return ""
        return attack_sqlmap(target)
    launch_anim("SQLMap", "💉")
    url = target if target.startswith('http') else f"http://{target}"
    cmd = get_cli_prefix() + ['sqlmap', '-u', url, '--batch', '--level=2', '--risk=2']
    info(f"Launching: {' '.join(cmd)}")
    try: subprocess.Popen(cmd); ok("SQLMap launched in new process"); return "SQLMap launched"
    except: fail("Failed to launch SQLMap"); return ""

def attack_metasploit():
    if not check_tool('msfconsole'): fail("Metasploit not installed"); return ""
    launch_anim("Metasploit", "💀")
    try: subprocess.Popen(['msfconsole']); ok("msfconsole launched"); return "Metasploit launched"
    except: fail("Failed to launch"); return ""

# ════════════════════════════════════════════════
#  MENUS
# ════════════════════════════════════════════════
def set_target():
    global TARGET, TARGET_IP, TARGET_FOLDER
    section("SET TARGET", "🎯")
    t = input(f"  {CYN}Enter IP or Domain: {RST}").strip()
    if not t: warn("No target entered"); return
    TARGET = t
    TARGET_IP = resolve_ip(t) or ""
    TARGET_FOLDER = make_target_folder(t)
    ok(f"Target: {BOLD}{TARGET}{RST} | IP: {BOLD}{TARGET_IP or 'Unknown'}{RST}")
    ok(f"Output folder: {CYN}{TARGET_FOLDER}/{RST}")
    with open(os.path.join(TARGET_FOLDER, "_target_info.json"), "w") as f:
        json.dump({"target": TARGET, "ip": TARGET_IP, "set_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tor": USE_TOR}, f, indent=2)
    input(f"\n{DIM}Enter to continue...{RST}")

def recon_menu():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("RECONNAISSANCE", "🔍")
    numbered_list(["Website Title & Status", "NSLookup", "DNS Enumeration (A/MX/NS/TXT)", "dnsx (Advanced DNS)", "WHOIS Lookup", "Run ALL Recon", "Back"], CYN)
    sep()
    ch = prompt("RECON")
    if ch == "1": attack_website_title(TARGET)
    elif ch == "2": attack_nslookup(TARGET)
    elif ch == "3": attack_dns_enum(TARGET)
    elif ch == "4": attack_dnsx(TARGET)
    elif ch == "5": attack_whois(TARGET)
    elif ch == "6":
        info("Running ALL recon...")
        attack_website_title(TARGET); attack_nslookup(TARGET); attack_dns_enum(TARGET); attack_dnsx(TARGET); attack_whois(TARGET)
        ok("ALL recon complete.")
    input(f"\n{DIM}Enter to continue...{RST}")

def osint_menu():
    if not TARGET_IP: fail("Resolve target IP first!"); input(f"  {DIM}Enter...{RST}"); return
    section("OSINT", "👁")
    numbered_list(["Shodan Lookup", "Censys Lookup", "Run ALL OSINT", "Back"], CYN)
    sep()
    ch = prompt("OSINT")
    if ch == "1": attack_shodan(TARGET_IP)
    elif ch == "2": attack_censys(TARGET_IP)
    elif ch == "3":
        attack_shodan(TARGET_IP); attack_censys(TARGET_IP)
        ok("ALL OSINT complete.")
    input(f"\n{DIM}Enter to continue...{RST}")

def portscan_menu():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("PORT & NETWORK", "🛡")
    numbered_list(["RustScan (Ultra-Fast)", "Nmap Fast Scan (Top 100 + OS)", "Nmap FULL Scan (All 65535 ports)", "Run ALL Port Scans", "Back"], CYN)
    sep()
    ch = prompt("SCAN")
    if ch == "1": attack_rustscan(TARGET)
    elif ch == "2": attack_nmap(TARGET)
    elif ch == "3": attack_nmap_full(TARGET)
    elif ch == "4":
        attack_rustscan(TARGET); attack_nmap(TARGET)
        ok("ALL port scans complete.")
    input(f"\n{DIM}Enter to continue...{RST}")

def webattack_menu():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("WEB & SSL", "🔓")
    numbered_list(["Nikto Web Scanner", "httpx Tech Detection", "Nuclei Vulnerability Scanner", "WPScan (WordPress)", "Run ALL Web Attacks", "Back"], CYN)
    sep()
    ch = prompt("WEB")
    if ch == "1": attack_nikto(TARGET)
    elif ch == "2": attack_httpx(TARGET)
    elif ch == "3": attack_nuclei(TARGET)
    elif ch == "4": attack_wpscan(TARGET)
    elif ch == "5":
        attack_nikto(TARGET); attack_httpx(TARGET); attack_nuclei(TARGET); attack_wpscan(TARGET)
        ok("ALL web attacks complete.")
    input(f"\n{DIM}Enter to continue...{RST}")

def enum_menu():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("SUBDOMAIN & DIRECTORY", "🕸")
    numbered_list(["Subfinder Subdomain Discovery", "Gobuster Directory Brute Force", "FFUF Fast Web Fuzzer", "Run ALL Enum Attacks", "Back"], CYN)
    sep()
    ch = prompt("ENUM")
    if ch == "1": attack_subfinder(TARGET)
    elif ch == "2": attack_gobuster(TARGET)
    elif ch == "3": attack_ffuf(TARGET)
    elif ch == "4":
        attack_subfinder(TARGET); attack_gobuster(TARGET); attack_ffuf(TARGET)
        ok("ALL enum attacks complete.")
    input(f"\n{DIM}Enter to continue...{RST}")

def heavy_menu():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("HEAVY / EXPLOITATION", "💀")
    numbered_list(["SQLMap (SQL Injection)", "Metasploit Framework (msfconsole)", "Back"], RED)
    sep()
    ch = prompt("HEAVY")
    if ch == "1": attack_sqlmap(TARGET)
    elif ch == "2": attack_metasploit()
    input(f"\n{DIM}Enter to continue...{RST}")

def full_pipeline():
    if not TARGET: fail("Set a target first!"); input(f"  {DIM}Enter...{RST}"); return
    section("FULL AUTOMATED PIPELINE", "⚡")
    info("Phase 1: Recon & OSINT")
    attack_website_title(TARGET); attack_nslookup(TARGET); attack_dnsx(TARGET); attack_whois(TARGET)
    if TARGET_IP: attack_shodan(TARGET_IP); attack_censys(TARGET_IP)
    info("Phase 2: Port Scanning")
    attack_rustscan(TARGET); attack_nmap(TARGET)
    info("Phase 3: Web & Enum")
    attack_nikto(TARGET); attack_httpx(TARGET); attack_nuclei(TARGET); attack_wpscan(TARGET)
    attack_subfinder(TARGET); attack_gobuster(TARGET); attack_ffuf(TARGET)
    generate_markdown_report()
    ok(f"{BOLD}PIPELINE COMPLETE{RST} | All results saved to {CYN}{TARGET_FOLDER}/{RST}")
    input(f"\n{DIM}Enter to continue...{RST}")

def check_tools_dashboard():
    section("TOOL AVAILABILITY & AUTO-FIX", "🔧")
    tools = [
        ("nmap", "Port Scanner", "https://nmap.org"),
        ("rustscan", "Ultra-Fast Scanner", "https://github.com/RustScan/RustScan"),
        ("nikto", "Web Scanner", "https://github.com/sullo/nikto"),
        ("nuclei", "Vuln Scanner", "https://github.com/projectdiscovery/nuclei"),
        ("subfinder", "Subdomain Enum", "https://github.com/projectdiscovery/subfinder"),
        ("gobuster", "Dir Brute", "https://github.com/OJ/gobuster"),
        ("ffuf", "Web Fuzzer", "https://github.com/ffuf/ffuf"),
        ("httpx", "HTTP Prober", "https://github.com/projectdiscovery/httpx"),
        ("dnsx", "DNS Toolkit", "https://github.com/projectdiscovery/dnsx"),
        ("wpscan", "WordPress Scanner", "https://github.com/wpscanteam/wpscan"),
        ("sqlmap", "SQL Injection", "https://github.com/sqlmapproject/sqlmap"),
        ("proxychains4", "Tor Proxy", "https://github.com/haad/proxychains"),
    ]
    installed = sum(1 for name, _, _ in tools if check_tool(name))
    for name, desc, url in tools:
        if check_tool(name): 
            ok(f"{name:<18} INSTALLED  {DIM}{desc}{RST}")
        else: 
            fail(f"{name:<18} NOT FOUND  {DIM}{desc}{RST}")
            print(f"                  {CYN}↳ Get it: {url}{RST}")
    sep()
    pct = int((installed/len(tools))*100)
    bar = f"{GRN}█{RST}"*int(30*installed/len(tools)) + f"{DIM}░{RST}"*(30-int(30*installed/len(tools)))
    print(f"\n{BOLD}Readiness: {bar} {installed}/{len(tools)} ({pct}%){RST}")
    print(f"  {YLW}[F]{RST}  Auto-Fix ALL Missing Tools")
    print(f"  {YLW}[B]{RST}  Back to Main Menu")
    ch = prompt("FIX").upper()
    if ch == "F": auto_fix_all_missing()

def view_target_folder():
    section("TARGET OUTPUT FILES", "📂")
    if not TARGET_FOLDER or not os.path.exists(TARGET_FOLDER):
        warn("No target folder yet."); input(f"  {DIM}Enter...{RST}"); return
    ok(f"Folder: {CYN}{TARGET_FOLDER}/{RST}"); sep()
    files = sorted(os.listdir(TARGET_FOLDER))
    if not files: warn("No output files yet.")
    else:
        for f in files:
            size = os.path.getsize(os.path.join(TARGET_FOLDER, f))
            print(f"    {GRN}├──{RST} {f}  {DIM}({size/1024:.1f}KB){RST}")
    input(f"\n{DIM}Enter to continue...{RST}")

# ════════════════════════════════════════════════
#  MAIN MENU
# ════════════════════════════════════════════════
def main():
    global TARGET, TARGET_IP, TARGET_FOLDER
    clear(); banner()
    print(f"  {CYN}Initializing systems...{RST}"); time.sleep(0.5)
    
    while True:
        clear(); banner()
        tor_st = f"{GRN}{BOLD}◉ ON{RST}" if USE_TOR else f"{RED}○ OFF{RST}"
        print(f"  {CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RST}")
        status("Target",  f"{BOLD}{TARGET or f'{DIM}Not Set'}{RST}", "ok" if TARGET else "fail")
        status("IP",      f"{BOLD}{TARGET_IP or f'{DIM}Not Set'}{RST}", "ok" if TARGET_IP else "fail")
        status("Tor",     tor_st, "ok" if USE_TOR else "fail")
        status("Output",  f"{CYN}{TARGET_FOLDER or f'{DIM}Not Set'}{RST}" if TARGET_FOLDER else f"{DIM}Not Set{RST}", "ok" if TARGET_FOLDER else "warn")
        print(f"  {CYN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RST}")
        print(f"""
{MGN}   1{RST}  Set Target (IP / Domain)
{MGN}   2{RST}  Tor & IP Rotation
{MGN}   3{RST}  Reconnaissance Attacks
{MGN}   4{RST}  OSINT Attacks (Shodan / Censys)
{MGN}   5{RST}  Port & Network Attacks (RustScan / Nmap)
{MGN}   6{RST}  Web & SSL Attacks (Nikto / Nuclei / WPScan)
{MGN}   7{RST}  Subdomain & Directory Attacks (Gobuster / FFUF)
{MGN}   8{RST}  Heavy / Exploitation Attacks
{MGN}   9{RST}  Full Automated Pipeline + Markdown Report
{MGN}  10{RST}  Check Tools & Auto-Fix Missing Dependencies
{MGN}  11{RST}  View Target Output Files
{MGN}  12{RST}  Clear Target Output Folder
{MGN}   0{RST}  Exit
""")
        ch = prompt("USH")
        if ch == "1": set_target()
        elif ch == "2": tor_submenu()
        elif ch == "3": recon_menu()
        elif ch == "4": osint_menu()
        elif ch == "5": portscan_menu()
        elif ch == "6": webattack_menu()
        elif ch == "7": enum_menu()
        elif ch == "8": heavy_menu()
        elif ch == "9": full_pipeline()
        elif ch == "10": check_tools_dashboard()
        elif ch == "11": view_target_folder()
        elif ch == "12": clear_target_output()
        elif ch == "0":
            print(f"\n{RED}Disconnecting...{RST}"); time.sleep(0.2)
            print(f"  {GRN}Stay safe. Stay anonymous.{RST}\n")
            sys.exit(0)
        else:
            fail("Invalid choice"); input(f"\n{DIM}Enter...{RST}")

if __name__ == "__main__":
    main()