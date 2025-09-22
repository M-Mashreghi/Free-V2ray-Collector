import pybase64
import binascii
import os
import datetime
import sort
import save_config 
import time
from helpers import safe_get
# app.py (top of file)
import logging
from seperate_config_country import seperate_by_country
from update_git import Update,update_with_token
import os, logging, sys
from update_git import update_with_token

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "0") in ("1","true","True")
LOG_DIR = os.getenv("APP_LOG_DIR", "logs")

handlers = [logging.StreamHandler(sys.stdout)]
if LOG_TO_FILE:
    os.makedirs(LOG_DIR, exist_ok=True)
    handlers.append(logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=handlers,
)
logger = logging.getLogger("collector")




def generate_urls(base_url_format):
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime(base_url_format)
    # print(formatted_date)
    return formatted_date


def decode_base64(encoded):

    decoded = ''
    for encoding in ['utf-8', 'iso-8859-1']:
        try:
            decoded = pybase64.b64decode(encoded + b'=' * (-len(encoded) % 4)).decode(encoding)
            break
        except (UnicodeDecodeError, binascii.Error):
            pass
    return decoded


def generate_v2ray_configs(decoded_data):

    configs = []

    for config in decoded_data:
        configs.append(config)

    sorted_configs = sorted(configs)

    return sorted_configs


# def decode_links(links):
#     decoded_data = []
#     for link in links:
#         resp = safe_get(link)
#         if not resp:
#             print("error for", link)
#             continue

#         encoded_bytes = resp.content
#         # if check_not_be_old_data_bytes(link,encoded_bytes):
#         decoded_text = decode_base64(encoded_bytes)
#         lines = encoded_bytes.split(b'\n')
#         if len(lines) > 1 :
#             for line in lines:
#                 decoded_text = decode_base64(line)
#                 decoded_data.append(decoded_text)
#         else:
#             decoded_data.append(decoded_text)


#     sorted_configs = generate_v2ray_configs(decoded_data)

#     return sorted_configs

def decode_links(links):
    decoded_data = []
    for link in links:
        logger.info("Fetching: %s", link)
        resp = safe_get(link)
        if not resp:
            logger.warning("Failed to fetch %s", link)
            continue

        encoded_bytes = resp.content
        try:
            decoded_text = decode_base64(encoded_bytes)
        except Exception as e:
            logger.error("Base64 decode failed for %s ➜ %s", link, e)
            continue

        lines = encoded_bytes.split(b'\n')
        if len(lines) > 1:
            for line in lines:
                decoded_data.append(decode_base64(line))
        else:
            decoded_data.append(decoded_text)

    logger.info("Decoded %d configs from %d links", len(decoded_data), len(links))
    return generate_v2ray_configs(decoded_data)




def decode_dir_links(dir_links):
    decoded_dir_links = []
    for link in dir_links:
        resp = safe_get(link)
        if not resp:
            print("error for", link)
            continue
        decoded_dir_links.append(resp.text)
    return decoded_dir_links






def main():



    links = [
        'https://raw.githubusercontent.com/internet4jina/daily/main/studious',
        generate_urls("https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/%m%d.txt"),
        'https://proxypool.link/sip002/sub',
        'https://proxypool.link/ss/sub',
        'https://proxypool.link/vmess/sub',
        'https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt',
        'https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt',
        'https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray',
        'https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt',
        'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2',
        'https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription1',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription2',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription3',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription4',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription5',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription6',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription7',
        'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription8',
        'https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt',
        'https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub',
        'https://raw.githubusercontent.com/freefq/free/master/v2',
        'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2',
        'https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/main/submerge/converted.txt',
        'https://v2.alicivil.workers.dev/?list=1',
        'https://v2.alicivil.workers.dev/?list=2',
        'https://v2.alicivil.workers.dev/?list=3',
        'https://v2.alicivil.workers.dev/?list=4',
        'https://v2.alicivil.workers.dev/?list=5',
        'https://v2.alicivil.workers.dev/?list=6',
        'https://v2.alicivil.workers.dev/?list=8',
        'https://v2.alicivil.workers.dev/?list=7', 
               
    ]
    dir_links = [

        'https://raw.githubusercontent.com/ImMyron/V2ray/main/Telegram',
        'https://rentry.co/mohammad885/raw',
        'https://raw.githubusercontent.com/ShatakVPN/ConfigForge/main/configs/all.txt',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt',
        'https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all',
        'https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/refs/heads/main/all_configs.txt',
        'https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_sub_merge.txt',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt',
        'https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/all_extracted_configs.txt',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/splitted/ss.txt',
        'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/trojan.txt',
        'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/vmess.txt',
        'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt',
        ]

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)

    merged_configs = decoded_links + decoded_dir_links
    merged_configs = list(set(merged_configs))
    save_config.save_data(merged_configs)
    shuffled_config , shuffled_list = sort.sort()
    save_config.save_data_shuffle(shuffled_config , shuffled_list)
    seperate_by_country()
    # Update()
    update_with_token()




if __name__ == "__main__":
    logger.info("Starting collector run")
    while True:
        main()
        time.sleep(3 * 60 * 60)
    logger.info("It went sleep")

