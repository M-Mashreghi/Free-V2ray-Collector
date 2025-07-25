# ========== helpers.py ==========
import requests, logging

# یک سشن مشترک با retry
_session = requests.Session()
_session.mount(
    "https://",
    requests.adapters.HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=3, backoff_factor=1, status_forcelist=[502, 503, 504]
        )
    ),
)

def safe_get(url: str, *, timeout: int = 10):
    """GET با هندل‌کردن همهٔ خطاهای شبکه‌ای؛ None برمی‌گرداند اگر موفق نشود."""
    try:
        r = _session.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; FreeCollector/1.0)"},
        )
        r.raise_for_status()
        return r
    except requests.exceptions.SSLError as e:
        logging.warning("SSL error for %s ➜ %s", url, e)
    except requests.exceptions.RequestException as e:
        logging.warning("Request error for %s ➜ %s", url, e)
    return None
