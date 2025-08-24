import os
import base64
from tqdm import tqdm
import re
import json
import requests
import get_loc
import random
import save_config
import pycountry

# Pick ONE random colored heart per config
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
    heart = random.choice(HEARTS)
    # Keep it short and URL-friendly; trailing space helps readability after '#'
    return f"@Xen2ray{heart} "

def replace_name_1(url: str):
    name_tag = _new_name()
    try:
        if url.startswith("vmess://"):
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

        else:
            return re.sub(r'#.*', f'#{name_tag}', url)
    except Exception:
        return None

def ensure_directory_exists(file_path):
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

def sort():
    # Use CURRENT working directory consistently
    ptt = os.getcwd()

    vmess_file = os.path.join(ptt, "Splitted-By-Protocol/vmess.txt")
    vless_file = os.path.join(ptt, "Splitted-By-Protocol/vless.txt")
    trojan_file = os.path.join(ptt, "Splitted-By-Protocol/trojan.txt")
    ss_file = os.path.join(ptt, "Splitted-By-Protocol/ss.txt")
    ssr_file = os.path.join(ptt, "Splitted-By-Protocol/ssr.txt")

    # Ensure directories exist
    for fp in (vmess_file, vless_file, trojan_file, ss_file, ssr_file):
        ensure_directory_exists(fp)
        open(fp, "w").close()

    vmess_list, vless_list, trojan_list, ss_list, ssr_list = [], [], [], [], []
    new_configs = []

    # Read All_Configs_Sub.txt from CURRENT folder (matches save_config.py)
    full_file_path = os.path.join(ptt, "All_Configs_Sub.txt")
    with open(full_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for config in tqdm(lines):
        cfg = replace_name_1(config.strip())
        if cfg:
            new_configs.append(cfg)

    # Deduplicate
    all_config = list(set(new_configs))

    for config in tqdm(all_config):
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
        except Exception:
            pass

    # Deduplicate each
    vmess_list = list(set(vmess_list))
    vless_list = list(set(vless_list))
    trojan_list = list(set(trojan_list))
    ss_list = list(set(ss_list))
    ssr_list = list(set(ssr_list))

    # Flatten and shuffle
    all_list = list(set(vmess_list + ss_list + trojan_list + vless_list + ssr_list))
    shuffled_list = random.sample(all_list, len(all_list))

    # Write outputs (base64 for vless/trojan/ss/ssr as in your original file)
    open(vmess_file, "w", encoding="utf-8").write("\n".join(vmess_list))
    open(vless_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(vless_list).encode("utf-8")).decode("utf-8"))
    open(trojan_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(trojan_list).encode("utf-8")).decode("utf-8"))
    open(ss_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(ss_list).encode("utf-8")).decode("utf-8"))
    open(ssr_file, "w", encoding="utf-8").write(base64.b64encode("\n".join(ssr_list).encode("utf-8")).decode("utf-8"))

    shuffled_config = "\n".join(shuffled_list)
    return shuffled_config, shuffled_list
