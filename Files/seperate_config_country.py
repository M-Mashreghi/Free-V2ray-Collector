import os
from typing import Optional
import get_loc  # reuse your resolvers & cache

INPUT_FILENAME = "All_shuffled_config.txt"
OUTPUT_DIR = "Config_by_country"

def _flag_to_alpha2(text: str) -> Optional[str]:
    """Find the LAST flag emoji in text and convert to ISO-2 (e.g., 🇩🇪 -> DE)."""
    if not text:
        return None
    codepoints = [ord(ch) for ch in text]
    # Regional Indicator range: U+1F1E6..U+1F1FF
    ris = [cp for cp in codepoints if 0x1F1E6 <= cp <= 0x1F1FF]
    if len(ris) < 2:
        return None
    # Use the last pair
    a, b = ris[-2], ris[-1]
    a_idx = a - 0x1F1E6
    b_idx = b - 0x1F1E6
    if 0 <= a_idx < 26 and 0 <= b_idx < 26:
        return chr(ord('A') + a_idx) + chr(ord('A') + b_idx)
    return None

def _alpha2_from_geo(line: str) -> Optional[str]:
    """
    Fallback: derive country via host->IP->(city, flag) using get_loc.
    Returns ISO-2 if we can resolve a flag, else None.
    """
    try:
        host = get_loc.extract_host_from_line(line)
        if not host:
            return None
        ip = get_loc._resolve_ip(host)  # cached in get_loc
        if not ip:
            return None
        city, flag = get_loc._lookup_city_flag(ip)  # cached; may be offline if GeoLite used
        if not flag:
            return None
        return _flag_to_alpha2(flag)
    except Exception:
        return None

def _country_code_for_line(line: str) -> str:
    # 1) Prefer explicit flag in the line
    cc = _flag_to_alpha2(line)
    if cc:
        return cc
    # 2) Fallback to geoloc from host/ip
    cc = _alpha2_from_geo(line)
    if cc:
        return cc
    # 3) Unknown
    return "UN"

def seperate_by_country():
    input_file_path = os.path.join(os.getcwd(), INPUT_FILENAME)
    if not os.path.exists(input_file_path):
        print(f"[seperate_by_country] File not found: {input_file_path}")
        return

    with open(input_file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if not lines:
        print("[seperate_by_country] No lines to process.")
        return

    grouped = {}
    for line in lines:
        cc = _country_code_for_line(line)
        grouped.setdefault(cc, []).append(line)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = 0
    for cc, group in grouped.items():
        out_fp = os.path.join(OUTPUT_DIR, f"server_{cc}.txt")
        with open(out_fp, "w", encoding="utf-8") as out:
            out.write("\n".join(group))
        total += len(group)

    print(f"Groups saved in '{OUTPUT_DIR}' folder. {len(grouped)} files, {total} lines total.")

if __name__ == "__main__":
    seperate_by_country()
