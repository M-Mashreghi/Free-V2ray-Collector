import os
import base64
from tqdm import tqdm
import re
import get_loc
import random
import save_config
import socket
from urllib.parse import urlsplit, parse_qs
import base64
import json as _json



import re
from urllib.parse import urlsplit

_SCHEME_DEFAULT_PORT = {
    "ss": 8388, "ssr": 8388,
    "trojan": 443, "vless": 443, "vmess": 443,
    "hysteria2": 443, "hy2": 443, "https": 443, "http": 80,
}


HEARTS = [
    "\u2764\uFE0F",  # ❤️
    "\U0001F499",    # 💙
    "\U0001F49A",    # 💚
    "\U0001F49B",    # 💛
    "\U0001F49C",    # 💜
    "\U0001F9E1",    # 🧡
    "\U0001F5A4",    # 🖤
    "\U0001F90E",    # 🤎
    "\U0001F90D",    # 🤍
]

def _new_name():
    return f"@Xen2ray{random.choice(HEARTS)} "



# Set to True if you want to resolve domains to IPs (slower but stricter)
RESOLVE_DNS = False



def _safe_host_port(url: str) -> tuple[str, int, str]:
    """
    Return (host, port, scheme) without raising ValueError on malformed ports.
    Falls back to scheme defaults; returns port=0 if unknown.
    """
    url = (url or "").strip()
    u = urlsplit(url)
    scheme = (u.scheme or "").lower()
    host = (u.hostname or "").strip()

    # Try the normal way first
    try:
        port = u.port  # may raise ValueError
    except ValueError:
        # Manually extract digits after ':' in netloc
        m = re.search(r":\s*(\d+)\b", u.netloc or "")
        port = int(m.group(1)) if m else None

    if port is None:
        port = _SCHEME_DEFAULT_PORT.get(scheme, 0)

    return host, int(port), scheme


def _safe_b64decode(s: str) -> bytes:
    # vmess payloads sometimes miss padding
    s = s.strip()
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def _extract_vmess_host(vmess_url: str) -> str | None:
    # vmess://<base64 json>
    try:
        payload_b64 = vmess_url.split("://", 1)[1]
        data = _safe_b64decode(payload_b64).decode("utf-8", errors="ignore")
        obj = _json.loads(data)
        host = (obj.get("add") or "").strip()
        # If SNI/Host header present, it might represent the actual server
        sni = (obj.get("sni") or obj.get("host") or "").strip()
        return sni or host or None
    except Exception:
        return None

def _extract_standard_host(url: str) -> str | None:
    # vless/trojan/ss/ssr/hysteria2: parse netloc, then strip userinfo and port
    try:
        u = urlsplit(url)
        host = u.hostname  # strips userinfo and port
        if not host:
            return None
        # hy2 sometimes includes 'sni' query; if present, it often indicates the true TLS host
        if u.scheme in ("vless", "trojan", "hysteria2"):
            q = parse_qs(u.query)
            sni = q.get("sni", [None])[0]
            if sni:
                return sni
        return host
    except Exception:
        return None

def _canonical_host(config: str) -> tuple[str, str] | None:
    """
    Returns a key like (scheme, canonical_host)
    canonical_host is either hostname or resolved IP (if RESOLVE_DNS=True).
    """
    try:
        scheme = config.split("://", 1)[0].lower()
        if scheme == "vmess":
            host = _extract_vmess_host(config)
        else:
            host = _extract_standard_host(config)
        if not host:
            return None
        host = host.strip().lower()
        if RESOLVE_DNS:
            try:
                host = socket.gethostbyname(host)
            except Exception:
                # keep hostname if resolution fails
                pass
        return (scheme, host)
    except Exception:
        return None


def _score_config_for_keep(cfg: str):
    host, port, scheme = _safe_host_port(cfg)

    # tls rank: prefer 443, 8443
    if port in (443, 8443):
        tls_rank = 0
    else:
        tls_rank = 1

    # port rank: prefer common ones
    if port in (80, 8080, 2052, 2082, 2086, 2095, 8443):
        port_rank = 0
    else:
        port_rank = 1

    # transport rank (example: maybe deduce from query/netloc)
    trans_rank = 0  # keep whatever logic you had before

    # scheme rank
    if scheme in ("trojan", "vless", "vmess", "ss", "hy2", "hysteria2"):
        scheme_rank = 0
    else:
        scheme_rank = 1

    length = len(cfg)

    return (tls_rank, port_rank, trans_rank, scheme_rank, length)




# def _score_config_for_keep(url: str) -> tuple:
#     """
#     Lower tuple wins. Prioritize TLS and common ports.
#     You can tweak the priorities freely.
#     """
#     u = urlsplit(url)
#     scheme = u.scheme.lower()

#     # Prefer TLS-ish configs
#     q = parse_qs(u.query)
#     security = (q.get("security", [""])[0] or q.get("type", [""])[0]).lower()

#     # Port pref: 443 best, then 8443, 80, others
#     port = u.port or 0
#     port_rank = {443: 0, 8443: 1, 80: 2}.get(port, 9)

#     # Prefer http/2 or ws over tcp (example heuristic)
#     transm = (q.get("type", [""])[0] or q.get("net", [""])[0]).lower()
#     trans_rank = {"h2": 0, "http": 1, "ws": 2, "grpc": 3, "tcp": 4}.get(transm, 5)

#     # Prefer vless/trojan over ss over vmess (purely an example—tune as you like)
#     scheme_rank = {"vless": 0, "trojan": 1, "ss": 2, "hysteria2": 3, "vmess": 4}.get(scheme, 5)

#     # Prefer TLS-like security
#     tls_rank = 0 if ("tls" in security or "reality" in security or "xtls" in security) else 1

#     # Finally, shorter URL (as a tie breaker), to avoid super-bloated params
#     length = len(url)

#     return (tls_rank, port_rank, trans_rank, scheme_rank, length)

def dedupe_by_server(configs: list[str]) -> list[str]:
    """
    Keep exactly one config per (scheme, canonical_host).
    Chosen by _score_config_for_keep priority.
    """
    buckets: dict[tuple[str, str], str] = {}
    for cfg in configs:
        key = _canonical_host(cfg)
        if not key:
            # If we can't parse a host, keep it using a unique fallback key
            buckets[(cfg.split("://", 1)[0].lower(), f"__raw__:{hash(cfg)}")] = cfg
            continue
        if key not in buckets:
            buckets[key] = cfg
        else:
            # decide which one to keep
            current = buckets[key]
            if _score_config_for_keep(cfg) < _score_config_for_keep(current):
                buckets[key] = cfg
    return list(buckets.values())



def replace_name_1(url: str):
    name_tag = _new_name()
    try:
        if url.startswith("vmess://"):
            # keep your location logic for vmess
            try:
                loc_name = get_loc.find_location_vmess(url, name_tag)
            except Exception:
                loc_name = name_tag
            return get_loc.update_vmess_name(url, loc_name)

        elif url.startswith("ss://"):
            try:
                loc_name = get_loc.find_loc_ss(url, name_tag)
            except Exception:
                loc_name = name_tag
            return re.sub(r'#.*', f'#{loc_name}', url)

        elif url.startswith("vless://"):
            try:
                loc_name = get_loc.find_loc_vless(url, name_tag)
            except Exception:
                loc_name = name_tag
            return re.sub(r'#.*', f'#{loc_name}', url)

        elif url.startswith("trojan://"):
            try:
                loc_name = get_loc.find_loc_trojan(url, name_tag)
            except Exception:
                loc_name = name_tag
            return re.sub(r'#.*', f'#{loc_name}', url)

        elif url.startswith("hysteria2://"):
            # no dedicated locator in your code—just tag it cleanly
            return re.sub(r'#.*', f'#{name_tag}', url) if '#' in url else f'{url}#{name_tag}'

        else:
            # other schemes: set/replace the fragment to our tag
            return re.sub(r'#.*', f'#{name_tag}', url) if '#' in url else f'{url}#{name_tag}'

    except Exception:
        return None

def ensure_directory_exists(file_path):
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)


def sort():
    ptt = os.getcwd()
    vmess_file = os.path.join(ptt, "Splitted-By-Protocol/vmess.txt")
    vless_file = os.path.join(ptt, "Splitted-By-Protocol/vless.txt")
    trojan_file = os.path.join(ptt, "Splitted-By-Protocol/trojan.txt")
    ss_file = os.path.join(ptt, "Splitted-By-Protocol/ss.txt")
    ssr_file = os.path.join(ptt, "Splitted-By-Protocol/ssr.txt")
    hy2_file   = os.path.join(ptt, "Splitted-By-Protocol/hysteria2.txt")

    for fp in (vmess_file, vless_file, trojan_file, ss_file, ssr_file,hy2_file):
        ensure_directory_exists(fp)
        open(fp, "w").close()

    new_configs = []

    full_file_path = os.path.join(ptt, "All_Configs_Sub.txt")
    with open(full_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove blanks/whitespace-only lines (and optionally keep only known schemes)
    lines = [c.strip() for c in lines if c and c.strip()]
    # (optional) keep only valid protocols:
    VALID = ("vmess://","vless://","trojan://","ss://","ssr://","hysteria2://")
    lines = [c for c in lines if c.startswith(VALID)]

    get_loc.prefetch_geo_for_configs(lines)  # <<< add this BEFORE the tqdm "Renaming configs" loop
    # 👇 Show progress bar with tqdm
    for config in tqdm(lines, desc="Renaming configs", unit="cfg"):
        cfg = replace_name_1(config.strip())
        if cfg:
            new_configs.append(cfg)

    # First: basic de-dupe by exact string
    all_config = list(set(new_configs))
    # Then: stronger de-dupe by "same server" (ignoring port/secret)
    all_config = dedupe_by_server(all_config)

    # bucket by protocol …
    vmess_list, vless_list, trojan_list, ss_list, ssr_list,hy2_list  = [], [], [], [], [], []



    for config in tqdm(all_config, desc="Sorting by protocol", unit="cfg"):
        try:
            if config.startswith("vmess://"):
                vmess_list.append(config)
            if config.startswith("vless://"):
                vless_list.append(config)
            if config.startswith("trojan://"):
                trojan_list.append(config)
            if config.startswith("ss://"):
                ss_list.append(config)
            if config.startswith("ssr://"):
                ssr_list.append(config)
            if config.startswith("hysteria2://") or config.startswith("hy2://"):
                hy2_list.append(config)
        except Exception:
            pass


    vmess_list = list(set(vmess_list))
    vless_list = list(set(vless_list))
    trojan_list = list(set(trojan_list))
    ss_list = list(set(ss_list))
    ssr_list = list(set(ssr_list))
    hy2_list = list(set(hy2_list))


    # Write outputs (base64 for vless/trojan/ss/ssr as in your original file)
    open(vmess_file, "w", encoding="utf-8").write("\n".join(vmess_list))
    open(vless_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(vless_list).encode("utf-8")).decode("utf-8"))
    open(trojan_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(trojan_list).encode("utf-8")).decode("utf-8"))
    open(ss_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(ss_list).encode("utf-8")).decode("utf-8"))
    open(ssr_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(ssr_list).encode("utf-8")).decode("utf-8"))
    open(hy2_file, "w", encoding="utf-8").write(
        base64.b64encode("\n".join(hy2_list).encode("utf-8")).decode("utf-8")
    )

    # Shuffle for downstream usage (unchanged)
    all_list = list(set(vmess_list + ss_list + trojan_list + vless_list + ssr_list + hy2_list))
    shuffled_list = random.sample(all_list, len(all_list))
    shuffled_config = "\n".join(shuffled_list)

    # ✅ OVERWRITE All_Configs_Sub.txt WITH RENAMED LINES
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_config))

    # ✅ OVERWRITE All_Configs_Sub.txt WITH RENAMED LINES
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_config))

    
    # Split merged configs into files with no more than 1000 configs per file
    with open(full_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    num_lines = len(lines)
    max_lines_per_file = 1000
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file
    for i in range(num_files):
        start_index = i * max_lines_per_file
        end_index = (i + 1) * max_lines_per_file
        filename = os.path.join(os.getcwd(), f'Sub{i+1}.conf')
        with open(filename, 'w', encoding='utf-8') as f:
            for line in lines[start_index:end_index]:
                f.write(line + '\n')
    

    return shuffled_config, shuffled_list