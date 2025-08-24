import json, os

def _alpha2_or_input(country: str) -> str:
    c = (country or "").strip()
    # If it already looks like a code, normalize to upper
    if len(c) == 2 and c.isalpha():
        return c.upper()

    # Try pycountry to resolve names/aliases to alpha-2
    try:
        import pycountry
        try:
            match = pycountry.countries.lookup(c)  # handles names, alpha_2, alpha_3, common aliases
            code = getattr(match, "alpha_2", None)
            if code:
                return code.upper()
        except LookupError:
            pass
    except Exception:
        pass

    # Last resort: return original string
    return c

def find_emoji(country_name: str) -> str:
    filename = "country_emojis.txt"

    # Try loading the mapping; if the file is missing or bad, fall back to code
    try:
        with open(filename, "r", encoding="utf-8") as f:
            country_emojis = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return _alpha2_or_input(country_name)

    # Direct hit
    if country_name in country_emojis:
        return country_emojis[country_name]

    # Try a few normalized keys
    candidates = {
        country_name,
        (country_name or "").strip(),
        (country_name or "").strip().title(),
        (country_name or "").strip().upper(),
    }
    for k in candidates:
        if k in country_emojis:
            return country_emojis[k]

    # Not found in file → return a country code
    return _alpha2_or_input(country_name)
