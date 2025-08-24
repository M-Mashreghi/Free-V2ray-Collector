import pybase64
import requests
import binascii
import os
import datetime
import sort
import save_config 
import base64
import flag
import time
from helpers import safe_get

from seperate_config_country import seperate_by_country
from Run import Update
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


# def check_not_be_old_data_bytes(link,encoded_bytes):
#     # Create a folder path for "websearch" if it doesn't exist
#     folder_name = "websearch"
#     if not os.path.exists(folder_name):
#         os.mkdir(folder_name)
    
#     # Construct the filename using the URL
#     filename = os.path.join(folder_name, link.split("//")[1].replace("/", "_") + ".txt")

#     # Read the previous content from the file
#     try:
#         with open(filename, "rb") as file:
#             previous_content = file.read()
#     except FileNotFoundError:
#         previous_content = b""  # If the file doesn't exist, set previous_content as empty bytes
    
#     # Compare the previous content with the new content
#     if previous_content == encoded_bytes:
#         # print(f"Content from {link} is the same as the previous content. Doing nothing.")
#         return False
#     else:
#         with open(filename, "wb") as file:
#             file.write(encoded_bytes)
#         # print(f"Content from {link} is different from the previous content. Saving new content to {filename}. You can perform some action here.")
#         return True



# def check_not_be_old_data_decoded(link,encoded_bytes):
#     # Create a folder path for "websearch" if it doesn't exist
#     folder_name = "websearch"
#     if not os.path.exists(folder_name):
#         os.mkdir(folder_name)
    
#     # Construct the filename using the URL
#     filename = os.path.join(folder_name, link.split("//")[1].replace("/", "_") + ".txt")

#     if os.path.exists(filename):
#         with open(filename, "r", encoding="utf-8") as file:
#             previous_text = file.read()
#     else:
#         previous_text = ""  # If the file doesn't exist, set previous_text as an empty string

#     # Compare the previous text with the new text
#     if previous_text == encoded_bytes:
#         # print(f"Text content from {link} is the same as the previous content. Doing nothing.")
#         return False
#     else:
#         with open(filename, "w", encoding="utf-8") as file:
#             file.write(encoded_bytes)
#         # print(f"Text content from {link} is different from the previous content. Saving new content to {filename}. You can perform some action here.")
#         return True
def decode_links(links):
    decoded_data = []
    for link in links:
        resp = safe_get(link)
        if not resp:
            print("error for", link)
            continue

        encoded_bytes = resp.content
        # if check_not_be_old_data_bytes(link,encoded_bytes):
        decoded_text = decode_base64(encoded_bytes)
        lines = encoded_bytes.split(b'\n')
        if len(lines) > 1 :
            for line in lines:
                decoded_text = decode_base64(line)
                decoded_data.append(decoded_text)
        else:
            decoded_data.append(decoded_text)


    sorted_configs = generate_v2ray_configs(decoded_data)

    return sorted_configs




# def decode_links(links):

#     decoded_data = []

#     for link in links:
#         try:

#             response = requests.get(link)
#             encoded_bytes = response.content
#             # if check_not_be_old_data_bytes(link,encoded_bytes):
#             decoded_text = decode_base64(encoded_bytes)
#             lines = encoded_bytes.split(b'\n')
#             if len(lines) > 1 :
#                 for line in lines:
#                     decoded_text = decode_base64(line)
#                     decoded_data.append(decoded_text)
#             else:
#                 decoded_data.append(decoded_text)

#         except:
#             print("error for" , link)

#     sorted_configs = generate_v2ray_configs(decoded_data)

#     return sorted_configs


# def decode_dir_links(dir_links):


#     decoded_dir_links = []

#     for link in dir_links:

#         response = requests.get(link)
#         decoded_text = response.text
#         # if check_not_be_old_data_decoded(link,decoded_text):
#         decoded_dir_links.append(decoded_text)

#     return decoded_dir_links

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
        # 'https://raw.githubusercontent.com/internet4jina/daily/main/studious',
        # 'https://raw.githubusercontent.com/HenryPorternew/sbs/main/ssb/sw',
        # generate_urls("https://nodefree.org/dy/%Y/%m/%Y%m%d.txt"),
        # generate_urls("https://clashnode.com/wp-content/uploads/%Y/%m/%Y%m%d.txt"),
        # generate_urls("https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/%m%d.txt"),
        # 'https://proxypool.link/sip002/sub',
        # 'https://proxypool.link/ss/sub',
        # 'https://proxypool.link/vmess/sub',
        # 'https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt',
        # 'https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt',
        # 'https://mrpooya.xyz/api/ramezan/fastRay.php?sub=1',
        # 'https://mrpooya.xyz/api/ramezan/GreenNet.php?sub=1',
        # 'https://kxswa.tk/v2ray',
        # 'https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray',
        # 'https://raw.fastgit.org/freefq/free/master/v2',
        # 'https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt',
        'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2',
        # 'https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free',
        # 'https://raw.githubusercontent.com/vveg26/get_proxy/main/dist/v2ray.config.txt',
        # 'https://tt.vg/freev2',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription1',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription2',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription3',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription4',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription5',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription6',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription7',
        # 'https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription8',
        # 'https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt',
        # 'https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub',
        # 'https://raw.githubusercontent.com/freefq/free/master/v2',
        # 'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2'
        # 'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/mix',
        # 'https://v2.alicivil.workers.dev/?list=1',
        # 'https://v2.alicivil.workers.dev/?list=2',
        # 'https://v2.alicivil.workers.dev/?list=3',
        # 'https://v2.alicivil.workers.dev/?list=4',
        # 'https://v2.alicivil.workers.dev/?list=5',
        # 'https://v2.alicivil.workers.dev/?list=6',
        # 'https://v2.alicivil.workers.dev/?list=8',
        'https://v2.alicivil.workers.dev/?list=7',        
    ]
    dir_links = [



        'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/reality',
        # 'https://raw.githubusercontent.com/ImMyron/V2ray/main/Telegram',
        # 'https://rentry.co/mohammad885/raw',
        # 'https://raw.githubusercontent.com/ImMyron/V2ray/main/Web',
        # 'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix',
        # 'https://vpn.fail/free-proxy/v2ray',
        # 'https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config',
        # 'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt',
        # 'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/mix',
        # 'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/donated',
        # 'https://raw.githubusercontent.com/sashalsk/V2Ray/main/V2Ray-list-current',
        # 'https://raw.githubusercontent.com/RenaLio/Mux2sub/main/z_textlist',
        # 'https://raw.githubusercontent.com/abshare/abshare.github.io/main/README.md'
        # 'https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all',
        # 'https://raw.githubusercontent.com/baipiao250/HigeFreeProxies/master/sub/sub_merge.txt',
        # 'https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_sub_merge.txt',
        # 'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt',
        # 'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/splitted/ss.txt',
        # 'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/trojan.txt',
        # 'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/vmess.txt',
        'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt'

    ]

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)

    merged_configs = decoded_links + decoded_dir_links
    merged_configs = list(set(merged_configs))
    save_config.save_data(merged_configs)
    print("saved_configs")
    shuffled_config , shuffled_list = sort.sort()
    save_config.save_data_shuffle(shuffled_config , shuffled_list)
    seperate_by_country()
    Update()




if __name__ == "__main__":
    while True:
        main()
        # Sleep for 12 hours (in seconds)
        time.sleep(12* 60 * 60)

