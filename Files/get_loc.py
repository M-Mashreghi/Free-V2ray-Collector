# get_loc.py
import requests
from ip2geotools.databases.noncommercial import DbIpCity
import re, base64, json, socket, os 
from functools import lru_cache
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from emoji import find_emoji
import logging
logger = logging.getLogger("get_loc")
import geoip2.database
_GEO_CITY_DB = geoip2.database.Reader("GeoLite2-City.mmdb")


def _city_flag_from_ip(ip: str) -> tuple[str, str]:
    """Return (city, flag) fully offline from GeoLite2-City.mmdb"""
    if not ip:
        return "", ""
    try:
        resp = _GEO_CITY_DB.city(ip)
        city = (resp.city.name or "").strip()
        cc   = (resp.country.iso_code or "").strip()
        return city, find_emoji(cc)
    except Exception as e:
        logger.debug("GeoLite2 lookup failed for %s: %s", ip, e)
        return "", ""

@lru_cache(maxsize=100000)
def _lookup_city_flag(ip: str) -> tuple[str, str]:
    if not ip or not is_valid_ip(ip):
        return "", ""

    # ✅ offline lookup first
    city, flag = _city_flag_from_ip(ip)
    if city or flag:
        return city, flag

    # optional: keep ip-api fallback if city missing
    # ...
    return "", ""



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

def _resolve_many(hosts: list[str], workers: int | None = None) -> dict[str, str]:
    """
    Resolve many hostnames safely on restricted hosts.
    - Worker count is capped and can be overridden by env GEO_RESOLVE_WORKERS.
    - Falls back to sequential resolution if threads cannot be started.
    """
    out: dict[str, str] = {}
    if not hosts:
        return out

    # cap workers aggressively; default to 8, clamp to [2, 16]
    max_workers = workers or int(os.getenv("GEO_RESOLVE_WORKERS", "8"))
    max_workers = max(2, min(max_workers, 16))

    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="geo-res") as ex:
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
    except RuntimeError:
        # e.g. "can't start new thread" – fall back to sequential mode
        for h in hosts:
            try:
                ip = _resolve_ip(h)
                if ip:
                    out[h] = ip
            except Exception:
                pass
        return out
    
# def _resolve_many(hosts: list[str], workers: int = 50) -> dict[str, str]:
#     out: dict[str, str] = {}
#     with ThreadPoolExecutor(max_workers=workers) as ex:
#         futs = {ex.submit(_resolve_ip, h): h for h in hosts}
#         for fut in as_completed(futs):
#             h = futs[fut]
#             try:
#                 ip = fut.result()
#                 if ip:
#                     out[h] = ip
#             except Exception:
#                 pass
#     return out

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

