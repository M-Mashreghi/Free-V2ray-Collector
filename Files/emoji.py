# emoji.py
from typing import Dict
import pycountry



country_emojis = {
    "US": "\U0001F1FA\U0001F1F8",
    "GB": "\U0001F1EC\U0001F1E7", 
    "DE": "\U0001F1E9\U0001F1EA",
    "FR": "\U0001F1EB\U0001F1F7",
    "ES": "\U0001F1EA\U0001F1F8",
    "IT": "\U0001F1EE\U0001F1F9",
    "JP": "\U0001F1EF\U0001F1F5",
    "CN": "\U0001F1E8\U0001F1F3",
    "RU": "\U0001F1F7\U0001F1FA",
    "CA": "\U0001F1E8\U0001F1E6",
    "AU": "\U0001F1E6\U0001F1FA",
    "BR": "\U0001F1E7\U0001F1F7",
    "IN": "\U0001F1EE\U0001F1F3",
    "KR": "\U0001F1F0\U0001F1F7",
    "MX": "\U0001F1F2\U0001F1FD",
    "NL": "\U0001F1F3\U0001F1F1",
    "SE": "\U0001F1F8\U0001F1EA",
    "CH": "\U0001F1E8\U0001F1ED",
    "TR": "\U0001F1F9\U0001F1F7",
    "ZA": "\U0001F1FF\U0001F1E6",
    "AR": "\U0001F1E6\U0001F1F7",
    "EG": "\U0001F1EA\U0001F1EC",
    "GR": "\U0001F1EC\U0001F1F7",
    "PT": "\U0001F1F5\U0001F1F9",
    "TH": "\U0001F1F9\U0001F1ED",
    "SG": "\U0001F1F8\U0001F1EA",
    "CA": "\U0001F1E8\U0001F1E6",
    "NZ": "\U0001F1F3\U0001F1FF",
    "IE": "\U0001F1EE\U0001F1EA",
    "NO": "\U0001F1F3\U0001F1F4",
    "FI": "\U0001F1EB\U0001F1EE",
    "BE": "\U0001F1E7\U0001F1EA",
    "DK": "\U0001F1E9\U0001F1F0",
    "SE": "\U0001F1F8\U0001F1EA",
    "PL": "\U0001F1F5\U0001F1F1",
    "UA": "\U0001F1FA\U0001F1E6",
    "HU": "\U0001F1ED\U0001F1FA",
    "AT": "\U0001F1E6\U0001F1F9",
    "CZ": "\U0001F1E8\U0001F1FF",
    "CH": "\U0001F1E8\U0001F1ED",
    "FI": "\U0001F1EB\U0001F1EE",
    "IE": "\U0001F1EE\U0001F1EA",
    "NO": "\U0001F1F3\U0001F1F4",
    "ZA": "\U0001F1FF\U0001F1E6",
    "AR": "\U0001F1E6\U0001F1F7",
    "EG": "\U0001F1EA\U0001F1EC",
    "GR": "\U0001F1EC\U0001F1F7",
    "PT": "\U0001F1F5\U0001F1F9",
    "TH": "\U0001F1F9\U0001F1ED",
    "SG": "\U0001F1F8\U0001F1EA",
    "CA": "\U0001F1E8\U0001F1E6",
    "NZ": "\U0001F1F3\U0001F1FF",
    "IE": "\U0001F1EE\U0001F1EA",
    "NO": "\U0001F1F3\U0001F1F4",
    "FI": "\U0001F1EB\U0001F1EE",
    "BE": "\U0001F1E7\U0001F1EA",
    "IR": "\U0001F1EE\U0001F1F7",  # Iran
    "UA": "\U0001F1FA\U0001F1E6",  # Ukraine
    "MY": "\U0001F1F2\U0001F1FE",  # Malaysia
    "ZA": "\U0001F1FF\U0001F1E6",  # South Africa
    "RU": "\U0001F1F7\U0001F1FA",  # Russia
    "SA": "\U0001F1F8\U0001F1E6",  # Saudi Arabia
    "AE": "\U0001F1E6\U0001F1EA",  # United Arab Emirates
    "EG": "\U0001F1EA\U0001F1EC",  # Egypt
    "GR": "\U0001F1EC\U0001F1F7",  # Greece
    "KR": "\U0001F1F0\U0001F1F7",  # South Korea
    "TH": "\U0001F1F9\U0001F1ED",  # Thailand
    "IT": "\U0001F1EE\U0001F1F9",  # Italy
    "ES": "\U0001F1EA\U0001F1F8",  # Spain
    "SG": "\U0001F1F8\U0001F1EA",  # Singapore
    "MY": "\U0001F1F2\U0001F1FE",  # Malaysia
    "NL": "\U0001F1F3\U0001F1F1",  # Netherlands
    "PL": "\U0001F1F5\U0001F1F1",  # Poland
    "AT": "\U0001F1E6\U0001F1F9",  # Austria
    "CZ": "\U0001F1E8\U0001F1FF",  # Czech Republic
    "HU": "\U0001F1ED\U0001F1FA",  # Hungary
    "DK": "\U0001F1E9\U0001F1F0",  # Denmark
    "RO": "\U0001F1F7\U0001F1F4",  # Romania
    "CH": "\U0001F1E8\U0001F1ED",  # Switzerland
    "NO": "\U0001F1F3\U0001F1F4",  # Norway
    "SE": "\U0001F1F8\U0001F1EA",  # Sweden
    "FI": "\U0001F1EB\U0001F1EE",  # Finland
    "IE": "\U0001F1EE\U0001F1EA",  # Ireland
    "BE": "\U0001F1E7\U0001F1EA",  # Belgium
    "LU": "\U0001F1F1\U0001F1FA",  # Luxembourg
    "IS": "\U0001F1EE\U0001F1F8",  # Iceland
    "GR": "\U0001F1EC\U0001F1F7",  # Greece
    "PT": "\U0001F1F5\U0001F1F9",  # Portugal
    "SI": "\U0001F1F8\U0001F1EE",  # Slovenia
    "BG": "\U0001F1E7\U0001F1EC",  # Bulgaria
    "HR": "\U0001F1ED\U0001F1F7",  # Croatia
    "RS": "\U0001F1F7\U0001F1F8",  # Serbia
    "AL": "\U0001F1E6\U0001F1F1",  # Albania
    "MK": "\U0001F1F2\U0001F1F0",  # North Macedonia
    "ME": "\U0001F1F2\U0001F1EA",  # Montenegro
    "BA": "\U0001F1E6\U0001F1E6",  # Bosnia and Herzegovina
    "XK": "\U0001F1FD\U0001F1F0",  # Kosovo
    "MD": "\U0001F1F2\U0001F1E9",  # Moldova
    "BY": "\U0001F1E7\U0001F1FE",  # Belarus
    "LT": "\U0001F1F1\U0001F1F9",  # Lithuania
    "LV": "\U0001F1F1\U0001F1FB",  # Latvia
    "EE": "\U0001F1EA\U0001F1EA",  # Estonia
    "MT": "\U0001F1F2\U0001F1F9",  # Malta
    "CY": "\U0001F1E8\U0001F1FE",  # Cyprus
    "MC": "\U0001F1F2\U0001F1E8",  # Monaco
    "AD": "\U0001F1E6\U0001F1E9",  # Andorra
    "SM": "\U0001F1F8\U0001F1F2",  # San Marino
    "VA": "\U0001F1FB\U0001F1E6",  # Vatican City
    "LI": "\U0001F1F1\U0001F1EE",  # Liechtenstein
    "MQ": "\U0001F1F2\U0001F1F6",  # Martinique
    "GP": "\U0001F1EC\U0001F1F5",  # Guadeloupe
    "RE": "\U0001F1F7\U0001F1EA",  # Réunion
    "YT": "\U0001F1FE\U0001F1F9",  # Mayotte
    "GF": "\U0001F1EC\U0001F1EB",  # French Guiana
    "PF": "\U0001F1F5\U0001F1EB",  # French Polynesia
    "NC": "\U0001F1F3\U0001F1E8",  # New Caledonia
    "TF": "\U0001F1F9\U0001F1EB",  # French Southern Territories
    "GL": "\U0001F1EC\U0001F1F1",  # Greenland
    "FO": "\U0001F1EB\U0001F1F4",  # Faroe Islands
    "IS": "\U0001F1EE\U0001F1F8",  # Iceland
    "AX": "\U0001F1E6\U0001F1FD",  # Åland Islands
    "KI": "\U0001F1F0\U0001F1EE",  # Kiribati
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "KI": "\U0001F1F0\U0001F1EE",  # Kiribati
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "FM": "\U0001F1EB\U0001F1F2",  # Micronesia
    "MH": "\U0001F1F2\U0001F1ED",  # Marshall Islands
    "NR": "\U0001F1F3\U0001F1F7",  # Nauru
    "PW": "\U0001F1F5\U0001F1FC",  # Palau
    "TV": "\U0001F1F9\U0001F1FB",  # Tuvalu
    "WS": "\U0001F1FC\U0001F1F8",  # Samoa
    "TO": "\U0001F1F9\U0001F1F4",  # Tonga
    "VU": "\U0001F1FB\U0001F1FA",  # Vanuatu
    "North Holland": "\U0001F1F3\U0001F1F1",  # Netherlands
    "Hesse":"🏴󠁤󠁥󠁨󠁥󠁿",
    "Saxony":"🏴󠁤󠁥󠁨󠁥󠁿",
    "Bavaria": "\U0001F1F9\U0001F1FB",  # Netherlands

}


def _flag_from_alpha2(code: str) -> str:
    code = (code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return code
    base = 0x1F1E6  # Regional Indicator 'A'
    return chr(base + ord(code[0]) - ord('A')) + chr(base + ord(code[1]) - ord('A'))

# --- Build a mapping in the format you want: {"DE": "🇩🇪", "Germany": "🇩🇪", ...} ---
country_emojis: Dict[str, str] = {}

for c in pycountry.countries:
    code = c.alpha_2
    flag = _flag_from_alpha2(code)
    # Map the code and common names to the flag
    country_emojis[code] = flag
    country_emojis[c.name] = flag
    if getattr(c, "official_name", None):
        country_emojis[c.official_name] = flag
    if getattr(c, "common_name", None):
        country_emojis[c.common_name] = flag

# Handy aliases & regional names you mentioned (tweak as you like)
country_emojis.update({
    "USA": country_emojis["US"],
    "United States of America": country_emojis["US"],
    "UK": country_emojis["GB"],
    "South Korea": country_emojis["KR"],
    "North Korea": _flag_from_alpha2("KP"),
    "Russia": country_emojis["RU"],
    "Viet Nam": country_emojis["VN"],
    "Turkey": country_emojis["TR"],
    "Palestine": _flag_from_alpha2("PS"),

    # Regions → parent country flags
    "Bavaria": country_emojis["DE"],
    "Hesse": country_emojis["DE"],
    "Saxony": country_emojis["DE"],
    "North Holland": country_emojis["NL"],
})

def find_emoji(country_or_code: str) -> str:
    """Return flag emoji if known; otherwise return a country code fallback."""
    if not country_or_code:
        return ""

    cand = {
        country_or_code,
        country_or_code.strip(),
        country_or_code.strip().title(),
        country_or_code.strip().upper(),
    }
    for k in cand:
        if k in country_emojis:
            return country_emojis[k]

    # Try pycountry lookup (handles names, alpha2, alpha3)
    try:
        m = pycountry.countries.lookup(country_or_code)
        return country_emojis.get(m.alpha_2, _flag_from_alpha2(m.alpha_2))
    except LookupError:
        pass

    # If it looks like a 2-letter code, synthesize the flag even if not in dict
    cc = country_or_code.strip().upper()
    if len(cc) == 2 and cc.isalpha():
        return _flag_from_alpha2(cc)

    # Final fallback: just return the normalized code/text
    return cc
