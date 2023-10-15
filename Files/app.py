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


def decode_links(links):

    decoded_data = []

    for link in links:
        try:

            response = requests.get(link)
            encoded_bytes = response.content
            decoded_text = decode_base64(encoded_bytes)
            lines = encoded_bytes.split(b'\n')
            if len(lines) > 1 :
                for line in lines:
                    decoded_text = decode_base64(line)
                    decoded_data.append(decoded_text)
                
            else:
                decoded_data.append(decoded_text)

        except:
            print("error for" , link)

    sorted_configs = generate_v2ray_configs(decoded_data)

    return sorted_configs


def decode_dir_links(dir_links):


    decoded_dir_links = []

    for link in dir_links:
        response = requests.get(link)
        decoded_text = response.text
        decoded_dir_links.append(decoded_text)

    return decoded_dir_links


def main():
    links = [
        'https://raw.githubusercontent.com/HenryPorternew/sbs/main/ssb/sw',
        generate_urls("https://nodefree.org/dy/%Y/%m/%Y%m%d.txt"),
        generate_urls("https://clashnode.com/wp-content/uploads/%Y/%m/%Y%m%d.txt"),
        generate_urls("https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/%m%d.txt"),
        'https://proxypool.link/sip002/sub',
        'https://proxypool.link/ss/sub',
        'https://proxypool.link/vmess/sub',
        'https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt',
        'https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt',
        'https://mrpooya.xyz/api/ramezan/fastRay.php?sub=1',
        'https://mrpooya.xyz/api/ramezan/GreenNet.php?sub=1',
        'https://kxswa.tk/v2ray',
        'https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray',
        'https://raw.fastgit.org/freefq/free/master/v2',
        'https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt',
        'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2',
        'https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/free',
        'https://raw.githubusercontent.com/vveg26/get_proxy/main/dist/v2ray.config.txt',
        'https://tt.vg/freev2',
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
        'https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2'



    ]
    dir_links = [
        'https://vpn.fail/free-proxy/v2ray',
        'https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt',
        'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/mix',
        'https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/donated',
        'https://raw.githubusercontent.com/sashalsk/V2Ray/main/V2Ray-list-current',
        'https://raw.githubusercontent.com/RenaLio/Mux2sub/main/z_textlist',
        'https://raw.githubusercontent.com/abshare/abshare.github.io/main/README.md'
        'https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all',
        'https://raw.githubusercontent.com/baipiao250/HigeFreeProxies/master/sub/sub_merge.txt',
        'https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_sub_merge.txt',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt',
        'https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/splitted/ss.txt',
        'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/trojan.txt',
        'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/vmess.txt',
        'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt'

    ]

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)
    lines = []
    try:
        with open('test.txt', '+r') as file:
            # Read all lines from the file into a list
            lines = file.readlines()
    except:
        print("file not found")
    merged_configs = decoded_links + decoded_dir_links + lines
    merged_configs = list(set(merged_configs))
    save_config.save_data(merged_configs)
    shuffled_config , shuffled_list = sort.sort()
    save_config.save_data_shuffle(shuffled_config , shuffled_list)
    Update()




if __name__ == "__main__":
    while True:
        main()
        # Sleep for 12 hours (in seconds)
        time.sleep(11 * 60 * 60)

