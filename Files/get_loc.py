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


countries = {'Aruba': 'AW', 'Afghanistan': 'AF', 'Angola': 'AO', 'Anguilla': 'AI', 'Åland Islands': 'AX', 'Albania': 'AL', 'Andorra': 'AD', 
'United Arab Emirates': 'AE', 'Argentina': 'AR', 'Armenia': 'AM', 'American Samoa': 'AS', 'Antarctica': 'AQ', 'French Southern Territories': 'TF', 'Antigua and Barbuda': 'AG', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ', 'Burundi': 'BI', 'Belgium': 'BE', 'Benin': 'BJ', 'Bonaire, Sint Eustatius and Saba': 'BQ', 'Burkina Faso': 'BF', 'Bangladesh': 'BD', 'Bulgaria': 'BG', 'Bahrain': 'BH', 'Bahamas': 'BS', 'Bosnia and Herzegovina': 'BA', 'Saint Barthélemy': 'BL', 'Belarus': 'BY', 'Belize': 'BZ', 'Bermuda': 'BM', 'Bolivia, Plurinational State of': 'BO', 'Brazil': 'BR', 'Barbados': 'BB', 'Brunei Darussalam': 'BN', 'Bhutan': 'BT', 'Bouvet Island': 'BV', 'Botswana': 'BW', 'Central African Republic': 'CF', 'Canada': 'CA', 'Cocos (Keeling) Islands': 'CC', 'Switzerland': 'CH', 'Chile': 'CL', 'China': 'CN', "Côte d'Ivoire": 'CI', 'Cameroon': 'CM', 'Congo, The Democratic Republic of the': 'CD', 'Congo': 'CG', 'Cook Islands': 'CK', 'Colombia': 'CO', 'Comoros': 'KM', 'Cabo Verde': 'CV', 'Costa Rica': 'CR', 'Cuba': 'CU', 'Curaçao': 'CW', 'Christmas Island': 'CX', 'Cayman Islands': 'KY', 'Cyprus': 'CY', 'Czechia': 'CZ', 'Germany': 'DE', 'Djibouti': 'DJ', 'Dominica': 'DM', 'Denmark': 'DK', 'Dominican Republic': 'DO', 'Algeria': 'DZ', 'Ecuador': 'EC', 'Egypt': 'EG', 'Eritrea': 'ER', 'Western Sahara': 'EH', 'Spain': 'ES', 'Estonia': 'EE', 'Ethiopia': 'ET', 'Finland': 'FI', 'Fiji': 'FJ', 'Falkland Islands (Malvinas)': 'FK', 'France': 'FR', 'Faroe Islands': 'FO', 'Micronesia, Federated States of': 'FM', 'Gabon': 'GA', 'United Kingdom': 'GB', 'Georgia': 'GE', 'Guernsey': 'GG', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Guinea': 'GN', 'Guadeloupe': 'GP', 'Gambia': 'GM', 'Guinea-Bissau': 'GW', 'Equatorial Guinea': 'GQ', 'Greece': 'GR', 'Grenada': 'GD', 'Greenland': 'GL', 'Guatemala': 'GT', 'French Guiana': 'GF', 'Guam': 'GU', 'Guyana': 'GY', 'Hong Kong': 'HK', 'Heard Island and McDonald Islands': 'HM', 'Honduras': 'HN', 'Croatia': 'HR', 'Haiti': 'HT', 'Hungary': 'HU', 'Indonesia': 'ID', 'Isle of Man': 'IM', 'India': 'IN', 'British Indian Ocean Territory': 'IO', 'Ireland': 'IE', 'Iran, Islamic Republic of': 'IR', 'Iraq': 'IQ', 'Iceland': 'IS', 'Israel': 'IL', 'Italy': 'IT', 'Jamaica': 'JM', 'Jersey': 'JE', 'Jordan': 'JO', 'Japan': 'JP', 'Kazakhstan': 'KZ', 'Kenya': 'KE', 'Kyrgyzstan': 'KG', 'Cambodia': 'KH', 'Kiribati': 'KI', 'Saint Kitts and Nevis': 'KN', 'Korea, Republic of': 'KR', 'Kuwait': 'KW', "Lao People's Democratic Republic": 'LA', 'Lebanon': 'LB', 'Liberia': 'LR', 'Libya': 'LY', 'Saint Lucia': 'LC', 'Liechtenstein': 'LI',
 'Sri Lanka': 'LK', 'Lesotho': 'LS', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 'Macao': 'MO', 'Saint Martin (French part)': 'MF', 'Morocco': 'MA', 'Monaco': 'MC', 'Moldova, Republic of': 'MD', 'Madagascar': 'MG', 'Maldives': 'MV', 'Mexico': 'MX', 'Marshall Islands': 'MH', 'North Macedonia': 'MK', 'Mali': 'ML', 'Malta': 'MT', 'Myanmar': 'MM', 'Montenegro': 'ME', 'Mongolia': 'MN', 'Northern Mariana Islands': 'MP', 'Mozambique': 'MZ', 'Mauritania': 'MR', 'Montserrat': 'MS', 'Martinique': 'MQ', 'Mauritius': 'MU', 'Malawi': 'MW', 'Malaysia': 'MY', 'Mayotte': 'YT', 'Namibia': 'NA', 'New Caledonia': 'NC', 'Niger': 'NE', 'Norfolk Island': 'NF', 'Nigeria': 'NG', 'Nicaragua': 'NI', 'Niue': 'NU', 'Netherlands': 'NL', 'Norway': 'NO', 'Nepal': 'NP', 'Nauru': 'NR', 'New Zealand': 'NZ', 'Oman': 'OM', 'Pakistan': 'PK', 'Panama': 'PA', 'Pitcairn': 'PN', 'Peru': 'PE', 'Philippines': 'PH', 'Palau': 'PW', 'Papua New Guinea': 'PG', 'Poland': 'PL', 'Puerto Rico': 'PR', "Korea, Democratic People's Republic of": 'KP', 'Portugal': 'PT', 'Paraguay': 'PY', 'Palestine, State of': 'PS', 'French Polynesia': 'PF', 'Qatar': 'QA', 'Réunion': 'RE', 'Romania': 'RO', 'Russian Federation': 'RU', 'Rwanda': 'RW', 'Saudi Arabia': 'SA', 'Sudan': 'SD', 'Senegal': 'SN', 'Singapore': 'SG', 'South Georgia and the South Sandwich Islands': 'GS', 'Saint Helena, Ascension and Tristan da Cunha': 'SH', 'Svalbard and Jan Mayen': 
'SJ', 'Solomon Islands': 'SB', 'Sierra Leone': 'SL', 'El Salvador': 'SV', 'San Marino': 'SM', 'Somalia': 'SO', 'Saint Pierre and Miquelon': 'PM', 'Serbia': 'RS', 'South Sudan': 'SS', 'Sao Tome and Principe': 'ST', 'Suriname': 'SR', 'Slovakia': 'SK', 'Slovenia': 'SI', 'Sweden': 'SE', 'Eswatini': 'SZ', 'Sint Maarten (Dutch part)': 'SX', 'Seychelles': 'SC', 'Syrian Arab Republic': 'SY', 'Turks and Caicos Islands': 'TC', 'Chad': 'TD', 'Togo': 'TG', 'Thailand': 'TH', 'Tajikistan': 'TJ', 'Tokelau': 'TK', 'Turkmenistan': 'TM', 'Timor-Leste': 'TL', 'Tonga': 'TO', 'Trinidad and Tobago': 'TT', 'Tunisia': 'TN', 'Turkey': 'TR', 'Tuvalu': 'TV', 
'Taiwan, Province of China': 'TW', 'Tanzania, United Republic of': 'TZ', 'Uganda': 'UG', 'Ukraine': 'UA', 'United States Minor Outlying Islands': 'UM', 'Uruguay': 'UY', 'United States': 'US', 'Uzbekistan': 'UZ', 'Holy See (Vatican City State)': 'VA', 'Saint Vincent and the Grenadines': 'VC', 'Venezuela, Bolivarian Republic of': 'VE', 'Virgin Islands, British': 'VG', 'Virgin Islands, U.S.': 'VI', 'Viet Nam': 'VN', 'Vanuatu': 'VU', 'Wallis and Futuna': 'WF', 'Samoa': 'WS', 'Yemen': 'YE', 'South Africa': 'ZA', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'}

# emoji1 = '\U0001F49A'
emoji2 = '\U0001F499'
# new_name = " @𝕏en2ray " + emoji2 + " "


# find_emoji(
def printDetails(ip,new_name):
    res = DbIpCity.get(ip, api_key="free")

    city = (getattr(res, "city", "") or "").strip()
    # DbIpCity.country is already alpha-2 in most cases; region sometimes carries a code too
    code_or_name = getattr(res, "country", None) or getattr(res, "region", "")
    flag = find_emoji(code_or_name)
    name = f"{new_name}{city} {flag}".strip()


    # name = new_name + res.city+ ' ' + countries.get(res.region, res.region)
    return name

def printDeails_2(ip_address ,new_name ):
     # Use the ip-api.com API to get geolocation information
     api_url = f"http://ip-api.com/json/{ip_address}"
     response = requests.get(api_url)
     if response.status_code == 200:
        geolocation_data = response.json()

        city = (geolocation_data.get("city") or "").strip()
        code_or_name = geolocation_data.get("countryCode") or geolocation_data.get("country") or ""
        flag = find_emoji(code_or_name)
        name = f"{new_name}{city} {flag}".strip()


        #  city = geolocation_data.get("city")
        #  country = geolocation_data.get("country")
        #  name = new_name  + city + ' ' + countries.get(country, country)
        return name
     else:
        raise ZeroDivisionError("This is a custom ZeroDivisionError") 

# def test_find_loc(ip_address,new_name):
#     try:
#         try:
#             try:
#                  return printDeails_2(ip_address,new_name)
#             except:
#                 return printDetails(ip_address,new_name)
#         except:
#              ip_add = socket.gethostbyname(ip_address)
#              return printDetails(ip_add,new_name)
#     except:
#           return new_name




import time, socket

def test_find_loc(ip_address, new_name):
    try:
        # first attempt
        try:
            # t0 = time.perf_counter()
            result = printDeails_2(ip_address, new_name)
            # elapsed = (time.perf_counter() - t0) * 1000.0
            # print(f"printDeails_2 took {elapsed:.2f} ms for {ip_address}")
            return result
        except Exception:
            # return new_name

            # second attempt
            try:
                t0 = time.perf_counter()
                result = printDetails(ip_address, new_name)
                elapsed = (time.perf_counter() - t0) * 1000.0
                print(f"printDetails took {elapsed:.2f} ms for {ip_address}")
                print(result)
                return result
            except Exception:
                # fallback with DNS resolution
                t0 = time.perf_counter()
                ip_add = socket.gethostbyname(ip_address)
                result = printDetails(ip_add, new_name)
                elapsed = (time.perf_counter() - t0) * 1000.0
                print(f"socket.gethostbyname + printDetails took {elapsed:.2f} ms for {ip_address}")
                return result
    except Exception:
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


