# get_loc.py
import re
import base64
import json
import socket
from functools import lru_cache
from urllib.parse import urlparse

import requests
from ip2geotools.databases.noncommercial import DbIpCity
from emoji import find_emoji

# -------------------------------
# Fast HTTP session (Keep-Alive)
# -------------------------------
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Xen2rayLoc/1.0"})
# keep response tiny & fast
IP_API_FIELDS = "status,country,countryCode,city"

# -------------------------------
# Utilities
# -------------------------------
IP_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")

def is_valid_ip(ip_str: str) -> bool:
    return bool(IP_RE.match(ip_str or ""))

def _b64decode_padded(s: str) -> bytes:
    s = (s or "").strip()
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s)

@lru_cache(maxsize=50000)
def _resolve_ip(host_or_ip: str) -> str | None:
    """Resolve hostname to IPv4 once; return IP if string is already an IP."""
    if not host_or_ip:
        return None
    val = host_or_ip.strip()
    if is_valid_ip(val):
        return val
    try:
        return socket.gethostbyname(val)
    except Exception:
        return None

@lru_cache(maxsize=50000)
def _lookup_city_flag(ip: str) -> tuple[str, str]:
    """
    Return (city, flag_emoji) for an IP.
    Tries ip-api (fast) then DbIpCity (fallback). Cached per IP.
    """
    if not ip or not is_valid_ip(ip):
        return "", find_emoji("")

    # 1) ip-api (fast)
    try:
        r = SESSION.get(
            f"http://ip-api.com/json/{ip}?fields={IP_API_FIELDS}",
            timeout=1.5,
        )
        if r.ok:
            data = r.json()
            if data.get("status") == "success":
                city = (data.get("city") or "").strip()
                # prefer code for reliable flags
                code_or_name = data.get("countryCode") or data.get("country") or ""
                flag = find_emoji(code_or_name)
                return city, flag
    except Exception:
        pass

    # 2) DbIpCity fallback
    try:
        res = DbIpCity.get(ip, api_key="free")
        city = (getattr(res, "city", "") or "").strip()
        # DbIpCity.country may be a name; region sometimes holds a code/name too
        code_or_name = getattr(res, "country", None) or getattr(res, "region", "")
        flag = find_emoji(code_or_name)
        return city, flag
    except Exception:
        pass

    # 3) Unknown
    return "", find_emoji("")

def _build_name(new_name: str, city: str, flag: str) -> str:
    city = (city or "").strip()
    flag = (flag or "").strip()
    parts = [new_name.rstrip()]
    if city:
        parts.append(city)
    if flag:
        parts.append(flag)
    return " ".join(parts).strip()

# -------------------------------
# Public helpers (kept compatible)
# -------------------------------
def printDetails(ip: str, new_name: str) -> str:
    """DbIpCity path (kept for compatibility) – now uses the cached lookup."""
    city, flag = _lookup_city_flag(ip)
    return _build_name(new_name, city, flag)

def printDeails_2(ip_address: str, new_name: str) -> str:
    """ip-api path (kept for compatibility) – now uses the cached lookup."""
    city, flag = _lookup_city_flag(ip_address)
    return _build_name(new_name, city, flag)

def test_find_loc(ip_address_or_host: str, new_name: str) -> str:
    """
    Fast path:
    - Resolve domain→IP once (cached)
    - Lookup city+flag once per IP (cached)
    """
    ip = _resolve_ip(ip_address_or_host)
    if not ip:
        return new_name
    city, flag = _lookup_city_flag(ip)
    return _build_name(new_name, city, flag)

# -------------------------------
# VMess name updater
# -------------------------------
def update_vmess_name(vmess_url: str, replace_name: str) -> str:
    """Decode vmess, replace ps (name), re-encode."""
    vmess_url = (vmess_url or "").strip()
    try:
        payload_b64 = vmess_url.split("://", 1)[1]
    except Exception:
        return vmess_url

    try:
        config_json = _b64decode_padded(payload_b64).decode("utf-8", errors="ignore")
        config = json.loads(config_json)
    except Exception:
        return vmess_url

    config["ps"] = replace_name

    try:
        updated_config_json = json.dumps(config, separators=(",", ":"), ensure_ascii=False)
        updated_b64 = base64.b64encode(updated_config_json.encode("utf-8")).decode("utf-8")
        return f"vmess://{updated_b64}"
    except Exception:
        return vmess_url

# -------------------------------
# Protocol-specific finders
# -------------------------------
def find_loc_trojan(config_str: str, new_name: str) -> str:
    """Find location for trojan:// – use IP if present, else hostname."""
    ip_match = re.search(r'(?P<ip>\d+\.\d+\.\d+\.\d+)', config_str or "")
    if ip_match:
        ip_address = ip_match.group("ip")
        return test_find_loc(ip_address, new_name)
    parsed = urlparse(config_str or "")
    host = parsed.hostname
    return test_find_loc(host, new_name) if host else new_name

def find_location_vmess(vmess_url: str, new_name: str) -> str:
    """Find location for vmess:// by decoding the JSON and using 'add'."""
    try:
        vmess_config_base64 = vmess_url.split("://", 1)[1]
        vmess_config_json = _b64decode_padded(vmess_config_base64).decode("utf-8", errors="ignore")
        vmess_config = json.loads(vmess_config_json)
        server_address = vmess_config.get("add")
        return test_find_loc(server_address, new_name) if server_address else new_name
    except Exception:
        return new_name

def find_loc_ss(config_str: str, new_name: str) -> str:
    """Find location for ss:// – try IP, else domain in @host:port."""
    ip_match = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str or "")
    if ip_match:
        return test_find_loc(ip_match.group(1), new_name)
    m = re.search(r'@([\w\.-]+):', config_str or "")
    return test_find_loc(m.group(1), new_name) if m else new_name

def find_loc_vless(config_str: str, new_name: str) -> str:
    """Find location for vless:// – try IP, else domain in @host:port."""
    ip_match = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str or "")
    if ip_match:
        return test_find_loc(ip_match.group(1), new_name)
    m = re.search(r'@([\w\.-]+):', config_str or "")
    return test_find_loc(m.group(1), new_name) if m else new_name
