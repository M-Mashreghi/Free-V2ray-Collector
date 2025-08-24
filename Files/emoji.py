# emoji.py
import json, os

def _alpha2_or_input(country: str) -> str:
    c = (country or "").strip()
    if len(c) == 2 and c.isalpha():
        return c.upper()
    try:
        import pycountry
        try:
            m = pycountry.countries.lookup(c)
            if getattr(m, "alpha_2", None):
                return m.alpha_2.upper()
        except LookupError:
            pass
    except Exception:
        pass
    return c

def find_emoji(country_name: str) -> str | None:
    filename = "country_emojis.txt"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            mapping = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No file? return the best-guess country code
        return _alpha2_or_input(country_name)

    # Direct and normalized lookups
    candidates = {
        country_name,
        (country_name or "").strip(),
        (country_name or "").strip().title(),
        (country_name or "").strip().upper(),
    }
    for k in candidates:
        if k in mapping:
            return mapping[k]

    # Not found -> return best-guess code
    return _alpha2_or_input(country_name)
