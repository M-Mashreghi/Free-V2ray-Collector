# get_loc.py
import re
import base64
import json
import socket
from functools import lru_cache
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from ip2geotools.databases.noncommercial import DbIpCity
from emoji import find_emoji


# get_loc.py  — only the relevant diffs shown
import re, base64, json, socket
from functools import lru_cache
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from emoji import find_emoji

# NEW: local GeoIP
import geoip2.database
_GEO_CITY_DB = geoip2.database.Reader("GeoLite2-City.mmdb")



# ---------------------------------
# Fast HTTP session & ip-api fields
# ---------------------------------
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Xen2rayLoc/1.1"})
IP_API_FIELDS = "status,country,countryCode,city"  # keep responses tiny

# ---------------------------------
# Regex / helpers
# ---------------------------------
IP_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
AT_HOST_RE = re.compile(r'@([\w\.-]+):')         # for ss/vless/etc "user@host:port"
INLINE_IP_RE = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)')

def is_valid_ip(ip_str: str) -> bool:
    return bool(IP_RE.match(ip_str or ""))

def _b64decode_padded(s: str) -> bytes:
    s = (s or "").strip()
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s)

# -----------------------
# Prefetch global cache
# -----------------------
# Maps IP -> (city, flag_emoji)
PREFETCH_CITY_FLAG: dict[str, tuple[str, str]] = {}

def _country_flag_from_ip(ip: str) -> tuple[str, str]:
    """Return (city, flag). With Country DB we return ('', flag)."""
    if not ip:
        return "", ""
    try:
        resp = _GEO_COUNTRY_DB.country(ip)
        cc = (resp.country.iso_code or "").strip()
        return "", find_emoji(cc)  # no city in the Country DB
    except Exception:
        return "", ""









# ---------------------------------
# Host/IP extraction from configs
# ---------------------------------
def _extract_host_vmess(line: str) -> str | None:
    try:
        payload = line.split("://", 1)[1]
        cfg = json.loads(_b64decode_padded(payload).decode("utf-8", errors="ignore"))
        return (cfg.get("add") or "").strip() or None
    except Exception:
        return None

def _extract_host_generic(line: str) -> str | None:
    # Try "scheme://host..." first
    try:
        u = urlparse(line)
        if u.hostname:
            return u.hostname
    except Exception:
        pass
    # Try "...@host:port" pattern (ss/vless often)
    m = AT_HOST_RE.search(line or "")
    if m:
        return m.group(1)
    return None

def extract_host_from_line(line: str) -> str | None:
    if not line:
        return None
    line = line.strip()
    if line.startswith("vmess://"):
        return _extract_host_vmess(line)
    # quick win: if an inline IP is present, return it (fast path)
    m = INLINE_IP_RE.search(line)
    if m:
        return m.group("ip")
    return _extract_host_generic(line)

# ---------------------------------
# DNS resolve (batched & cached)
# ---------------------------------
@lru_cache(maxsize=100000)
def _resolve_ip(host_or_ip: str) -> str | None:
    """Resolve hostname to IPv4 once; return IP if already an IP."""
    if not host_or_ip:
        return None
    v = host_or_ip.strip()
    if is_valid_ip(v):
        return v
    try:
        return socket.gethostbyname(v)
    except Exception:
        return None

def _resolve_many(hosts: list[str], workers: int = 50) -> dict[str, str]:
    out: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_resolve_ip, h): h for h in hosts}
        for fut in as_completed(futs):
            h = futs[fut]
            try:
                ip = fut.result()
                if ip:
                    out[h] = ip
            except Exception:
                pass
    return out

# ---------------------------------
# ip-api BULK lookup
# ---------------------------------
def _ip_api_batch(ips: list[str]) -> dict[str, tuple[str, str]]:
    """
    Query up to 100 IPs per POST /batch.
    Returns {ip: (city, flag)}
    """
    if not ips:
        return {}
    payload = [{"query": ip, "fields": IP_API_FIELDS} for ip in ips]
    try:
        r = SESSION.post("http://ip-api.com/batch", json=payload, timeout=4)
        if not r.ok:
            return {}
        results = r.json()
    except Exception:
        return {}

    out: dict[str, tuple[str, str]] = {}
    for ip, item in zip(ips, results):
        if not isinstance(item, dict):
            continue
        if item.get("status") == "success":
            city = (item.get("city") or "").strip()
            code_or_name = item.get("countryCode") or item.get("country") or ""
            flag = find_emoji(code_or_name)
            out[ip] = (city, flag)
    return out

def _ip_api_batch_many(ips: list[str], chunk_size: int = 100) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    n = len(ips)
    for i in range(0, n, chunk_size):
        chunk = ips[i:i + chunk_size]
        out.update(_ip_api_batch(chunk))
    return out

# ---------------------------------
# Public: prefetch everything once
# ---------------------------------
def prefetch_geo_for_configs(lines: list[str]) -> None:
    """
    Extract unique hosts/IPs from config lines, resolve to IPs,
    bulk query ip-api (in chunks), fill PREFETCH_CITY_FLAG.
    """
    # 1) Collect unique hosts
    hosts: set[str] = set()
    for ln in lines or []:
        h = extract_host_from_line((ln or "").strip())
        if h:
            hosts.add(h)

    if not hosts:
        return

    # 2) Resolve to IPs (parallel)
    host_to_ip = _resolve_many(list(hosts))
    ips = sorted(set(host_to_ip.values()))
    if not ips:
        return

    # 3) Bulk geolocate IPs
    ip_to_city_flag = _ip_api_batch_many(ips, chunk_size=100)

    # 4) Save into global prefetch cache
    PREFETCH_CITY_FLAG.update(ip_to_city_flag)

# ---------------------------------
# On-demand lookup (hits prefetch first)
# ---------------------------------
@lru_cache(maxsize=100000)
def _lookup_city_flag(ip: str) -> tuple[str, str]:
    """Return (city, flag) for IP. Prefer prefetch; else query, then fallback DbIpCity."""
    if not ip or not is_valid_ip(ip):
        return "", find_emoji("")
    # Prefetch win
    if ip in PREFETCH_CITY_FLAG:
        return PREFETCH_CITY_FLAG[ip]

    # Single ip-api call (tiny fields)
    try:
        r = SESSION.get(f"http://ip-api.com/json/{ip}?fields={IP_API_FIELDS}", timeout=1.5)
        if r.ok:
            data = r.json()
            if data.get("status") == "success":
                city = (data.get("city") or "").strip()
                code_or_name = data.get("countryCode") or data.get("country") or ""
                flag = find_emoji(code_or_name)
                return city, flag
    except Exception:
        pass

    # Fallback DbIpCity
    try:
        res = DbIpCity.get(ip, api_key="free")
        city = (getattr(res, "city", "") or "").strip()
        code_or_name = getattr(res, "country", None) or getattr(res, "region", "")
        flag = find_emoji(code_or_name)
        return city, flag
    except Exception:
        pass

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

# ---------------------------------
# Public helpers (kept compatible)
# ---------------------------------
def printDetails(ip: str, new_name: str) -> str:
    city, flag = _lookup_city_flag(ip)
    return _build_name(new_name, city, flag)

def printDeails_2(ip_address: str, new_name: str) -> str:
    city, flag = _lookup_city_flag(ip_address)
    return _build_name(new_name, city, flag)

def test_find_loc(ip_address_or_host: str, new_name: str) -> str:
    ip = _resolve_ip(ip_address_or_host)
    if not ip:
        return new_name
    city, flag = _lookup_city_flag(ip)
    return _build_name(new_name, city, flag)

# ---------------------------------
# VMess name updater (unchanged)
# ---------------------------------
def update_vmess_name(vmess_url: str, replace_name: str) -> str:
    vmess_url = (vmess_url or "").strip()
    try:
        payload_b64 = vmess_url.split("://", 1)[1]
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

# ---------------------------------
# Protocol-specific finders
# ---------------------------------
def find_loc_trojan(config_str: str, new_name: str) -> str:
    m = INLINE_IP_RE.search(config_str or "")
    if m:
        return test_find_loc(m.group("ip"), new_name)
    parsed = urlparse(config_str or "")
    host = parsed.hostname
    if not host:
        m2 = AT_HOST_RE.search(config_str or "")
        host = m2.group(1) if m2 else None
    return test_find_loc(host, new_name) if host else new_name

def find_location_vmess(vmess_url: str, new_name: str) -> str:
    try:
        payload = vmess_url.split("://", 1)[1]
        cfg = json.loads(_b64decode_padded(payload).decode("utf-8", errors="ignore"))
        server_address = cfg.get("add")
        return test_find_loc(server_address, new_name) if server_address else new_name
    except Exception:
        return new_name

def find_loc_ss(config_str: str, new_name: str) -> str:
    ipm = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str or "")
    if ipm:
        return test_find_loc(ipm.group(1), new_name)
    m = AT_HOST_RE.search(config_str or "")
    return test_find_loc(m.group(1), new_name) if m else new_name

def find_loc_vless(config_str: str, new_name: str) -> str:
    ipm = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str or "")
    if ipm:
        return test_find_loc(ipm.group(1), new_name)
    m = AT_HOST_RE.search(config_str or "")
    return test_find_loc(m.group(1), new_name) if m else new_name


# # get_loc.py — offline city+flag with prefetch
# import base64
# import json
# import re
# import socket
# from functools import lru_cache
# from urllib.parse import urlparse, urlsplit, parse_qs
# from concurrent.futures import ThreadPoolExecutor, as_completed

# from emoji import find_emoji

# try:
#     import geoip2.database
# except Exception:
#     geoip2 = None

# # add near the top of get_loc.py
# import os
# from pathlib import Path

# _GEOIP_DB_PATH = "GeoLite2-City.mmdb"


# def _candidate_db_paths() -> list[str]:
#     here = Path(__file__).resolve().parent
#     return [
#         _GEOIP_DB_PATH,                                 # explicit path or filename in CWD
#         str(here / "GeoLite2-City.mmdb"),               # same folder as get_loc.py
#         str(here.parent / "GeoLite2-City.mmdb"),        # parent folder
#         str(Path(os.getcwd()) / "GeoLite2-City.mmdb"),  # current working dir
#     ]




# IP_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
# AT_HOST_RE = re.compile(r'@([\w\.-]+)')

# def _to_flag(country_iso2: str) -> str:
#     try:
#         return find_emoji((country_iso2 or '').upper()) or ''
#     except Exception:
#         return ''

# def is_valid_ip(ip_str: str) -> bool:
#     return bool(IP_RE.match(ip_str or ""))

# @lru_cache(maxsize=100000)
# def _resolve_ip(host: str) -> str:
#     if not host:
#         return ''
#     if is_valid_ip(host):
#         return host
#     try:
#         infos = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)
#         if infos:
#             return infos[0][4][0]
#     except Exception:
#         pass
#     return ''

# _reader = None
# def _get_reader():
#     global _reader
#     if _reader is not None:
#         return _reader

#     if geoip2 is None:
#         raise RuntimeError("geoip2 not installed. Run: pip install geoip2")

#     last_err = None
#     for p in _candidate_db_paths():
#         try:
#             if p and os.path.exists(p):
#                 _reader = geoip2.database.Reader(p)
#                 return _reader
#         except Exception as e:
#             last_err = e

#     # If we get here, DB was not found anywhere
#     searched = "\n  - " + "\n  - ".join(_candidate_db_paths())
#     raise RuntimeError(
#         "GeoLite2-City.mmdb not found.\n"
#         "Set env GEOIP_DB to the full path or place the file next to get_loc.py.\n"
#         f"Searched:{searched}\n"
#         f"Last error: {last_err}"
#     )

# _warned_geoip = False

# @lru_cache(maxsize=100000)
# def _city_flag_from_ip(ip: str) -> tuple[str, str]:
#     global _warned_geoip
#     if not ip:
#         return '', ''
#     try:
#         reader = _get_reader()
#         resp = reader.city(ip)
#         city = (getattr(resp.city, "name", "") or "").strip()
#         cc = (getattr(resp.country, "iso_code", "") or "").strip()
#         return city, _to_flag(cc)
#     except Exception as e:
#         if not _warned_geoip:
#             _warned_geoip = True
#             print(f"[get_loc] GeoIP lookup failed (will return blanks). Reason: {e}")
#         return '', ''


# def extract_host_from_line(line: str) -> str | None:
#     if not line:
#         return None
#     # Standard URL parse first
#     try:
#         u = urlparse(line)
#         if u.hostname:
#             return u.hostname
#     except Exception:
#         pass
#     # Fallback for raw "...@host:port"
#     m = AT_HOST_RE.search(line)
#     if m:
#         return m.group(1)
#     return None

# def _city_flag_from_host(host: str) -> tuple[str, str]:
#     ip = _resolve_ip(host)
#     return _city_flag_from_ip(ip)

# def _compose_name(base: str, city: str, flag: str) -> str:
#     parts = [p for p in [base.strip(), city.strip() if city else '', flag.strip() if flag else ''] if p]
#     return ' '.join(parts)

# # -------------------------
# # vmess helpers
# # -------------------------
# _VM_PARSE_RE = re.compile(r'^vmess://(?P<b64>.+)$', re.IGNORECASE)

# def _safe_b64decode(s: str) -> bytes:
#     s = s.strip()
#     s += "=" * (-len(s) % 4)
#     return base64.urlsafe_b64decode(s.encode('utf-8'))

# def _safe_b64encode(b: bytes) -> str:
#     return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

# def _extract_vmess_host(vmess_url: str) -> str | None:
#     m = _VM_PARSE_RE.match(vmess_url or '')
#     if not m:
#         return None
#     try:
#         payload = json.loads(_safe_b64decode(m.group('b64')))
#     except Exception:
#         return None
#     # Prefer SNI/Host if present
#     for key in ('sni', 'host', 'add'):
#         h = (payload.get(key) or '').strip()
#         if h:
#             return h
#     return None

# # -------------------------
# # Public API (used by sort.py)
# # -------------------------
# def find_loc_ss(config_str: str, new_name: str) -> str:
#     host = extract_host_from_line(config_str)
#     city, flag = _city_flag_from_host(host) if host else ('','')
#     return _compose_name(new_name, city, flag)

# def find_loc_vless(config_str: str, new_name: str) -> str:
#     # allow hy2 SNI in query
#     host = extract_host_from_line(config_str)
#     if host:
#         city, flag = _city_flag_from_host(host)
#     else:
#         # try to read sni= from query if present
#         try:
#             u = urlsplit(config_str)
#             sni = (parse_qs(u.query).get("sni", [""])[0] or "").strip()
#             city, flag = _city_flag_from_host(sni) if sni else ('','')
#         except Exception:
#             city, flag = '',''
#     return _compose_name(new_name, city, flag)

# def find_loc_trojan(config_str: str, new_name: str) -> str:
#     host = extract_host_from_line(config_str)
#     city, flag = _city_flag_from_host(host) if host else ('','')
#     return _compose_name(new_name, city, flag)

# def find_location_vmess(vmess_url: str, new_name: str) -> str:
#     host = _extract_vmess_host(vmess_url) or extract_host_from_line(vmess_url)
#     city, flag = _city_flag_from_host(host) if host else ('','')
#     return _compose_name(new_name, city, flag)

# def update_vmess_name(vmess_url: str, new_name: str) -> str:
#     m = _VM_PARSE_RE.match(vmess_url or '')
#     if not m:
#         return vmess_url
#     try:
#         payload = json.loads(_safe_b64decode(m.group('b64')))
#     except Exception:
#         return vmess_url
#     payload['ps'] = new_name
#     new_b64 = _safe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
#     return f"vmess://{new_b64}"

# # -------------------------
# # Prefetch used by sort.sort()
# # -------------------------
# # IP -> (city, flag) cache for quick reuse
# PREFETCH_CITY_FLAG: dict[str, tuple[str, str]] = {}

# def prefetch_geo_for_configs(lines: list[str]) -> None:
#     """
#     Pre-resolve host->IP and lookup (city, flag) locally.
#     No network I/O (GeoLite2-City.mmdb only).
#     Safe to call with thousands of lines.
#     """
#     if not lines:
#         return

#     hosts = set()
#     for ln in lines:
#         ln = (ln or "").strip()
#         if not ln:
#             continue
#         # vmess has opaque payload; try vmess extractor first
#         if ln.startswith("vmess://"):
#             h = _extract_vmess_host(ln)
#             if h:
#                 hosts.add(h)
#         # generic host extraction
#         h2 = extract_host_from_line(ln)
#         if h2:
#             hosts.add(h2)

#         # hy2 may include ?sni=
#         try:
#             if ln.startswith("hysteria2://") or ln.startswith("hy2://"):
#                 u = urlsplit(ln)
#                 sni = (parse_qs(u.query).get("sni", [""])[0] or "").strip()
#                 if sni:
#                     hosts.add(sni)
#         except Exception:
#             pass

#     if not hosts:
#         return

#     # Resolve hosts -> IPs (local DNS)
#     def _to_ip(h: str) -> str:
#         return _resolve_ip(h)

#     # Parallel resolve to speed up large sets
#     host_to_ip: dict[str, str] = {}
#     with ThreadPoolExecutor(max_workers=32) as ex:
#         futs = {ex.submit(_to_ip, h): h for h in hosts}
#         for fut in as_completed(futs):
#             h = futs[fut]
#             try:
#                 ip = fut.result()
#                 if ip:
#                     host_to_ip[h] = ip
#             except Exception:
#                 pass

#     # Prefill IP -> (city, flag)
#     unique_ips = set(host_to_ip.values())
#     for ip in unique_ips:
#         city, flag = _city_flag_from_ip(ip)
#         if city or flag:
#             PREFETCH_CITY_FLAG[ip] = (city, flag)
