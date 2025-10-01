import os
from typing import Optional
import requests

BASE = os.environ.get('DENO_TOOLS_URL')

def url_encode(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.post(BASE.rstrip('/') + '/url/encode', data=text.encode('utf-8'), timeout=5)
        if r.status_code == 200:
            return r.json().get('data')
    except Exception:
        return None
    return None

def url_decode(text: str) -> Optional[str]:
    if not BASE:
        return None
    try:
        r = requests.post(BASE.rstrip('/') + '/url/decode', data=text.encode('utf-8'), timeout=5)
        if r.status_code == 200:
            return r.json().get('data')
    except Exception:
        return None
    return None
