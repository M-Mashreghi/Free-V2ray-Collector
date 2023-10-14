import re
import base64
import json
import requests
import socket
import requests
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
from urllib.parse import urlparse
from emoji import find_emoji
# emoji1 = '\U0001F49A'
emoji2 = '\U0001F499'
new_name = " @𝕏en2ray " + emoji2 + " "



def printDetails(ip,new_name):
    res = DbIpCity.get(ip, api_key="free")
    name = new_name + res.city+ ' ' + find_emoji(res.region)
    return name

def printDeails_2(ip_address ,new_name ):
     # Use the ip-api.com API to get geolocation information
     api_url = f"http://ip-api.com/json/{ip_address}"
     response = requests.get(api_url)
     if response.status_code == 200:
         geolocation_data = response.json()
         city = geolocation_data.get("city")
         country = geolocation_data.get("country")
         name = new_name  + city + ' ' + find_emoji(country)
         return name
     else:
          raise ZeroDivisionError("This is a custom ZeroDivisionError") 

def test_find_loc(ip_address,new_name):
    try:
        try:
            try:
                 return printDeails_2(ip_address,new_name)
            except:
                return printDetails(ip_address,new_name)
        except:
             ip_add = socket.gethostbyname(ip_address)
             return printDetails(ip_add,new_name)
    except:
          return new_name


def update_vmess_name(vmess_url, replace_name):
    # Decode the VMess URL
    vmess_url = vmess_url.strip()
    config_base64 = vmess_url.split("://")[1]
    config_json = base64.b64decode(config_base64).decode()

    # Parse the JSON configuration
    config = json.loads(config_json)

    # Update the name field
    config["ps"] = replace_name

    # Encode the updated configuration as base64
    updated_config_json = json.dumps(config)
    updated_config_base64 = base64.b64encode(updated_config_json.encode()).decode()

    # Create the new VMess URL
    new_vmess_url = f"vmess://{updated_config_base64}"

    return new_vmess_url



# Define a regular expression pattern for an IP address
ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

# Function to check if a string is a valid IP address
def is_valid_ip(ip_str):
    return bool(re.match(ip_pattern, ip_str))



def find_loc_trojan(config_str,new_name):
        # Use regular expressions to extract the IP address from the string
        ip_match = re.search(r'(?P<ip>\d+\.\d+\.\d+\.\d+)', config_str)
        if ip_match:
                ip_address = ip_match.group("ip")
                return test_find_loc(ip_address,new_name)
        else:
            # Parse the URL
            parsed_url = urlparse(config_str)
            # Extract the hostname (domain)
            domain = parsed_url.hostname
            return test_find_loc(domain,new_name)

def find_location_vmess(vmess_url,new_name):
    # Decode the VMess URL
    vmess_config_base64 = vmess_url.split("://")[1]
    vmess_config_json = base64.b64decode(vmess_config_base64).decode()
    vmess_config = json.loads(vmess_config_json)

    # Extract the server address (location)
    server_address = vmess_config.get("add")

    if server_address:
         return test_find_loc(server_address,new_name)
    else:
         return new_name

def find_loc_ss(config_str, new_name):
    # Use regular expressions to extract the IP address from the string
    ip_match = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str)
    if ip_match:
        ip_address = ip_match.group(1)
        return test_find_loc(ip_address, new_name)
    else:
        # Use re.search() to find the domain in the URL
        pattern = r'@([\w.-]+):'
        match = re.search(pattern, config_str)
        # Check if a match was found
        if match:
            domain = match.group(1)
            return test_find_loc(domain, new_name)
        else:
            return new_name


# print(find_loc_ss("ss://YWVzLTI1Ni1jZmI6ZUlXMERuazY5NDU0ZTZuU3d1c3B2OURtUzIwMXRRMEQ=@139.162.236.79:8099#%F0%9F%92%9A%20M@M%20%F0%9F%92%99", new_name))
def find_loc_vless(config_str,new_name):
        # Use regular expressions to extract the IP address from the string
        ip_match = re.search(r'@(\d+\.\d+\.\d+\.\d+)', config_str)

        if ip_match:
                ip_address = ip_match.group(1)
                return test_find_loc(ip_address,new_name)


