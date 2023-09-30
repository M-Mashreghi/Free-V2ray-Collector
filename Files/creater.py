import yaml
import re
import base64
import json
import requests
import get_loc
emoji1 = '\U0001F49A'
emoji2 = '\U0001F499'
new_name = emoji1 + " M@M " + emoji2 + " "



# Read the URLs from the text file
with open(r'H:\GIT project\yaml-creator\urls.txt', 'r') as file:
    urls = file.read().splitlines()

# Modify URLs
for i in range(len(urls)):
    url = urls[i]
    if url.startswith("vmess://"):
        try:
            name_vmess = get_loc.find_location_vmess(url,new_name)
        except:
            name_vmess = new_name
        urls[i] = get_loc.update_vmess_name(url,name_vmess)
    elif url.startswith("ss://"):
        try:
            name_ss = get_loc.find_loc_ss(url,new_name)
        except:
            name_ss = new_name
        urls[i] = re.sub(r'#.*', f'#{name_ss}', url)
    elif url.startswith("vless://"):
        try:
            name_vless = get_loc.find_loc_vless(url,new_name)
        except:
            name_vless = new_name
        urls[i] = re.sub(r'#.*', f'#{name_vless}', url)
    elif url.startswith("trojan://"):
        try:
            name_trojan = get_loc.find_loc_trojan(url,new_name)
        except:
            name_trojan = new_name
        urls[i] = re.sub(r'#.*', f'#{name_trojan}', url)
    else:
        urls[i] = re.sub(r'#.*', f'#{new_name}', url)

# Convert URLs to YAML format
yaml_data = {
    "configurations": [
        {
            "url": url
        }
        for url in urls
    ]
}

# Save the YAML data to a file
with open(r'H:\GIT project\yaml-creator\configurations.yaml', 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file)

# Create a .conf file and write the modified URLs
with open(r'H:\GIT project\yaml-creator\configurations.conf', 'w', encoding='utf-8') as conf_file:
    for modified_url in urls:
        conf_file.write(f"{modified_url}\n\n")
