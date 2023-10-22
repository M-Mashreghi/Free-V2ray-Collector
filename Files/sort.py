import requests
import os
import base64
from tqdm import tqdm
import re
import base64
import json
import requests
import get_loc
import random
import  save_config 
import pycountry
# emoji1 = '\U0001F49A'
emoji2 = '\U0001F499'
new_name =  "@Xen2ray" + emoji2 + " "


def replace_name(url):
     # Modify URLs
    # countries = {}
    # for country in pycountry.countries:
    #      countries[country.name] = country.alpha_2


    if url.startswith("vmess://"):
        try:
            name_vmess = get_loc.find_location_vmess(url,new_name)
        except:
            name_vmess = new_name
        return get_loc.update_vmess_name(url,name_vmess)
    elif url.startswith("ss://"):
        try:
            name_ss = get_loc.find_loc_ss(url,new_name)
        except:
            name_ss = new_name
        return re.sub(r'#.*', f'#{name_ss}', url)
    elif url.startswith("vless://"):
        try:
            name_vless = get_loc.find_loc_vless(url,new_name)
        except:
            name_vless = new_name
        return re.sub(r'#.*', f'#{name_vless}', url)
    elif url.startswith("trojan://"):
        try:
            name_trojan = get_loc.find_loc_trojan(url,new_name)
        except:
            name_trojan = new_name
        return re.sub(r'#.*', f'#{name_trojan}', url)
    else:
        return re.sub(r'#.*', f'#{new_name}', url)



def sort():
    ptt = os.path.abspath(os.path.join(os.getcwd(), '..'))
    vmess_file = os.path.join(ptt, 'Splitted-By-Protocol/vmess.txt')
    vless_file = os.path.join(ptt, 'Splitted-By-Protocol/vless.txt')
    trojan_file = os.path.join(ptt, 'Splitted-By-Protocol/trojan.txt')
    ss_file = os.path.join(ptt, 'Splitted-By-Protocol/ss.txt')
    ssr_file = os.path.join(ptt, 'Splitted-By-Protocol/ssr.txt')

    open(vmess_file, "w").close()
    open(vless_file, "w").close()
    open(trojan_file, "w").close()
    open(ss_file, "w").close()
    open(ssr_file, "w").close()

    vmess = ""
    vless = ""
    trojan = ""
    ss = ""
    ssr = ""
    vmess_list = []
    vless_list = []
    trojan_list = []
    ss_list = []
    ssr_list = []
    new_configs = []

    output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
    file_name = "All_shuffled_config.txt"
    full_file_path = os.path.join(output_folder, file_name)
    with open(full_file_path, 'r', encoding='utf-8') as file:
        # Read all lines from the file into a list
        cleaned_lines = file.readlines()

    output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
    file_name = "All_Configs_Sub.txt"
    full_file_path = os.path.join(output_folder, file_name)

    with open(full_file_path, 'r', encoding='utf-8') as f:
            line = f.readlines()

            
    for config in tqdm(line):
        new_configs.append(replace_name(config))
    all_config = new_configs + cleaned_lines
    all_config = list(set(all_config))
    for config in tqdm(all_config):
        # config = replace_name(config)
        if config.startswith("vmess://"):
            # print(config)
            config_new = config +'\n'
            vmess_list.append(config_new)
            # open(vmess_file, "a").write(config + "\n")     
        if config.startswith("vless"):
            vless_list.append(config)  
        if config.startswith("trojan://"):
            trojan_list.append(config)  
        if config.startswith("ss"):   
            ss_list.append(config)
        if config.startswith("ssr"):
            ssr_list.append(config)

    ssr_list = list(set(ssr_list))
    vless_list = list(set(vless_list)) 
    trojan_list = list(set(trojan_list)) 
    ss_list = list(set(ss_list))
    vmess_list = list(set(vmess_list))


    all_list = vmess_list + ss_list + trojan_list + vless_list + ssr_list
    vmess = '\n'.join([str(item) for item in vmess_list])
    vless = '\n'.join([str(item) for item in vless_list])
    trojan = '\n'.join([str(item) for item in trojan_list])
    ss = '\n'.join([str(item) for item in ss_list])
    ssr = '\n'.join([str(item) for item in ssr_list])
    
    shuffled_list = random.sample(all_list, len(all_list))

      
    open(vmess_file, "w").write(vmess)  
    open(vless_file, "w").write(base64.b64encode(vless.encode("utf-8")).decode("utf-8"))  
    open(trojan_file, "w").write(base64.b64encode(trojan.encode("utf-8")).decode("utf-8"))  
    open(ss_file, "w").write(base64.b64encode(ss.encode("utf-8")).decode("utf-8"))  
    open(ssr_file, "w").write(base64.b64encode(ssr.encode("utf-8")).decode("utf-8")) 
    shuffled_config = '\n'.join([str(item) for item in shuffled_list])

    return shuffled_config , shuffled_list
    

