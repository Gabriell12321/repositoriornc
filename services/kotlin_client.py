import os
from typing import Optional
import requests

BASE = os.environ.get('KOTLIN_UTILS_URL')

def get_qr_png(text: str, size: int = 256) -> Optional[bytes]:
    if not BASE:
        return None
    try:
        url = f"{BASE.rstrip('/')}/qr.png"
        resp = requests.get(url, params={"text": text, "size": size}, timeout=10)
        if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('image/png'):
            return resp.content
    except Exception:
        return None
    return None
